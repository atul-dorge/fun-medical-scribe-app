import requests
import os
import httpx
import logging
import time
from typing import Tuple, List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deepgram_transcription.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("deepgram_transcription")

# Load environment variables
try:
    dotenv_path = "../.env"
    load_dotenv(dotenv_path)
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    if not DEEPGRAM_API_KEY:
        raise ValueError("DEEPGRAM_API_KEY environment variable not found")
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.error(f"Error loading environment variables: {str(e)}")
    raise

# Deepgram API configuration
DEEPGRAM_URL = 'https://api.deepgram.com/v1/listen'
PARAMS = {
    'diarize': 'true',
    'punctuate': 'true',
    'model': 'nova-2',
    'language': 'hi',
}
HEADERS = {
    'Authorization': f'Token {DEEPGRAM_API_KEY}',
    'Content-Type': 'audio/mp4'
}


class DeepgramTranscriptionError(Exception):
    """Custom exception for Deepgram transcription errors"""
    pass


async def transcribe(audio_data) -> str:
    """
    Transcribe audio data using Deepgram API with diarization.

    Args:
        audio_data: Binary audio data

    Returns:
        str: Diarized transcript

    Raises:
        DeepgramTranscriptionError: If transcription fails
        httpx.TimeoutException: If request times out
        httpx.HTTPError: For HTTP-related errors
    """
    transcript = ''
    diarised_sentences = []
    current_speaker = None
    current_sentence = []

    if not audio_data:
        logger.error("Empty audio data provided")
        raise DeepgramTranscriptionError("Audio data is empty")

    logger.info(f"Starting transcription with parameters: {PARAMS}")
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  # 60 second timeout
            response = await client.post(
                DEEPGRAM_URL,
                params=PARAMS,
                headers=HEADERS,
                content=audio_data
            )

        # Check for HTTP errors
        response.raise_for_status()

        # Process response
        results = response.json()

        # Validate response structure
        if not results.get('results', {}).get('channels', []):
            logger.error(f"Invalid response structure: {results}")
            raise DeepgramTranscriptionError("Invalid API response structure")

        # Get words with speaker information
        try:
            words = results['results']['channels'][0]['alternatives'][0]['words']
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract words from response: {str(e)}")
            raise DeepgramTranscriptionError(f"Failed to extract words from response: {str(e)}")

        # Group words into sentences by speaker
        for word_info in words:
            try:
                speaker = word_info.get('speaker')
                word = word_info.get('punctuated_word', word_info.get('word', ''))

                # If speaker changed, flush the previous sentence
                if speaker != current_speaker and current_sentence:
                    diarised_sentences.append(
                        f"Speaker {current_speaker}: {' '.join(current_sentence)}."
                    )
                    current_sentence = []

                current_speaker = speaker
                current_sentence.append(word)
            except Exception as e:
                logger.warning(f"Error processing word: {str(e)}")
                continue

        # Add the last speaker's sentence
        if current_sentence:
            diarised_sentences.append(
                f"Speaker {current_speaker}: {' '.join(current_sentence)}."
            )

        # Final output string
        transcript = " ".join(diarised_sentences)

        elapsed_time = time.time() - start_time
        logger.info(f"Transcription completed successfully in {elapsed_time:.2f} seconds")
        logger.debug(f"Transcript: {transcript[:100]}...")  # Log first 100 chars of transcript

        return transcript

    except httpx.TimeoutException:
        elapsed_time = time.time() - start_time
        logger.error(f"Request timed out after {elapsed_time:.2f} seconds")
        raise DeepgramTranscriptionError("Transcription request timed out")

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_detail = e.response.text
        logger.error(f"HTTP error {status_code}: {error_detail}")

        # Provide more specific error messages based on status code
        if status_code == 401:
            raise DeepgramTranscriptionError("Authentication failed. Check your API key.")
        elif status_code == 400:
            raise DeepgramTranscriptionError(f"Bad request: {error_detail}")
        elif status_code == 429:
            raise DeepgramTranscriptionError("Rate limit exceeded. Try again later.")
        else:
            raise DeepgramTranscriptionError(f"API request failed with status {status_code}")

    except httpx.HTTPError as e:
        logger.error(f"HTTP request failed: {str(e)}")
        raise DeepgramTranscriptionError(f"HTTP request failed: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error during transcription: {str(e)}", exc_info=True)
        raise DeepgramTranscriptionError(f"Transcription failed: {str(e)}")


async def transcribe_file(file_path: str) -> str:
    """
    Helper function to transcribe an audio file from disk

    Args:
        file_path: Path to the audio file

    Returns:
        str: Transcription result
    """
    try:
        logger.info(f"Reading audio file: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        with open(file_path, 'rb') as f:
            audio_data = f.read()

        if not audio_data:
            logger.error(f"Empty audio file: {file_path}")
            raise DeepgramTranscriptionError("Audio file is empty")

        return await transcribe(audio_data)

    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error transcribing file: {str(e)}", exc_info=True)
        raise DeepgramTranscriptionError(f"File transcription failed: {str(e)}")


# Example usage
if __name__ == "__main__":
    import asyncio


    async def main():
        try:
            audio_file_path = "/path/to/your/audio/file.mp4"
            transcript = await transcribe_file(audio_file_path)
            print(f"Transcription result:\n{transcript}")
        except Exception as e:
            logger.error(f"Main execution failed: {str(e)}")
            print(f"Error: {str(e)}")


    asyncio.run(main())