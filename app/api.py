from dotenv import load_dotenv

load_dotenv()
import logging
import traceback
from typing import Dict, Any, Optional, Tuple
from fastapi import APIRouter, UploadFile, File, HTTPException, status
import json
import os
import uuid
import time
from abc import ABC, abstractmethod

# Set up more detailed logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Constants
TRANSCRIPT_FILE = "transcripts.txt"
AUDIO_DIR = "audio_uploads"

# Ensure directories exist at startup
try:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    logger.info(f"Ensured audio directory exists: {AUDIO_DIR}")
except Exception as e:
    logger.critical(f"Failed to create audio directory: {str(e)}")
    raise


# Environment Configuration using Singleton pattern
class EnvironmentConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnvironmentConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                logger.error("OPENAI_API_KEY environment variable not set")
                raise ValueError("OPENAI_API_KEY environment variable not set")

            self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
            if not self.deepgram_api_key:
                logger.error("DEEPGRAM_API_KEY environment variable not set")
                raise ValueError("DEEPGRAM_API_KEY environment variable not set")

            logger.info("Environment configuration loaded successfully")
        except Exception as e:
            logger.critical(f"Failed to load environment variables: {str(e)}")
            raise


# Abstract Factory Pattern for service creation
class ServiceFactory(ABC):
    @abstractmethod
    def create_llm_service(self):
        pass

    @abstractmethod
    def create_transcription_service(self):
        pass


# Concrete Factory implementation
class APIServiceFactory(ServiceFactory):
    def __init__(self, config: EnvironmentConfig):
        self.config = config

    def create_llm_service(self):
        from services import llm
        return llm.ChatGPT(api_key=self.config.openai_api_key)

    def create_transcription_service(self):
        from services import transcription
        return TranscriptionAdapter(transcription)


# Adapter Pattern for transcription service
class TranscriptionService(ABC):
    @abstractmethod
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        pass


class TranscriptionAdapter(TranscriptionService):
    def __init__(self, transcription_module):
        self.transcription_module = transcription_module

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        return await self.transcription_module.transcribe(audio_bytes)


# Strategy Pattern for prompts
class PromptStrategy(ABC):
    @abstractmethod
    def generate_prompt(self, transcripts: list) -> str:
        pass


class DefaultPromptStrategy(PromptStrategy):
    def generate_prompt(self, transcripts: list) -> str:
        from prompts import Prompts
        return Prompts.get_prompt_v1(transcripts)


# Storage Strategy Pattern
class StorageStrategy(ABC):
    @abstractmethod
    async def save_audio(self, audio_bytes: bytes, request_id: str) -> str:
        pass

    @abstractmethod
    def save_transcript(self, transcript: str) -> None:
        pass

    @abstractmethod
    def read_transcripts(self) -> list:
        pass


class FileStorageStrategy(StorageStrategy):
    async def save_audio(self, audio_bytes: bytes, request_id: str) -> str:
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)

        with open(audio_path, "wb") as audio_file:
            audio_file.write(audio_bytes)
        logger.info(f"[{request_id}] Audio file written to {audio_path}")
        return audio_path

    def save_transcript(self, transcript: str) -> None:
        with open(TRANSCRIPT_FILE, "a") as f:
            f.write(transcript + "\n")
        logger.info(f"Transcript saved to {TRANSCRIPT_FILE}")

    def read_transcripts(self) -> list:
        if not os.path.exists(TRANSCRIPT_FILE):
            logger.info(f"Transcript file not found: {TRANSCRIPT_FILE}")
            return []

        with open(TRANSCRIPT_FILE, "r") as f:
            return f.readlines()


# Service Locator Pattern
class ServiceLocator:
    _services = {}

    @classmethod
    def register(cls, service_name: str, service) -> None:
        cls._services[service_name] = service

    @classmethod
    def get(cls, service_name: str):
        return cls._services.get(service_name)


# Facade Pattern for audio processing
class AudioProcessingFacade:
    def __init__(
            self,
            transcription_service: TranscriptionService,
            storage: StorageStrategy
    ):
        self.transcription_service = transcription_service
        self.storage = storage

    async def process_audio(self, audio_bytes: bytes, request_id: str) -> str:
        # Save audio file
        await self.storage.save_audio(audio_bytes, request_id)

        # Transcribe audio
        transcript = await self.transcription_service.transcribe_audio(audio_bytes)
        logger.info(f"[{request_id}] Transcription completed successfully")

        # Save transcript
        self.storage.save_transcript(transcript)

        return transcript


# Notes Generator using Template Method Pattern
class NotesGenerator:
    def __init__(self, llm_service, prompt_strategy: PromptStrategy, storage: StorageStrategy):
        self.llm_service = llm_service
        self.prompt_strategy = prompt_strategy
        self.storage = storage

    async def generate_notes(self, request_id: str) -> Tuple[Optional[str], Optional[int]]:
        # Read transcripts
        transcripts = self.storage.read_transcripts()

        if not transcripts:
            logger.info(f"[{request_id}] No transcripts found")
            return None, None

        # Generate prompt
        prompt = self.prompt_strategy.generate_prompt(transcripts)
        logger.info(f"[{request_id}] Generated prompt for LLM")

        # Get LLM response
        notes, tokens = await self.llm_service.get_llm_response(prompt)
        logger.info(f"[{request_id}] Generated notes successfully, used {tokens} tokens")

        return notes, tokens


# Initialize services
try:
    config = EnvironmentConfig()
    service_factory = APIServiceFactory(config)

    llm_service = service_factory.create_llm_service()
    transcription_service = service_factory.create_transcription_service()
    storage = FileStorageStrategy()
    prompt_strategy = DefaultPromptStrategy()

    # Register services in locator
    ServiceLocator.register("llm_service", llm_service)
    ServiceLocator.register("transcription_service", transcription_service)
    ServiceLocator.register("storage", storage)

    # Create facades
    audio_processor = AudioProcessingFacade(transcription_service, storage)
    notes_generator = NotesGenerator(llm_service, prompt_strategy, storage)

    logger.info("All services initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize services: {str(e)}")
    raise

router = APIRouter()


@router.post("/upload/")
async def upload_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Handle audio file upload, transcribe it, and store the transcript.

    Args:
        file: Uploaded audio file

    Returns:
        Dict containing the transcript

    Raises:
        HTTPException: If any step in the process fails
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    logger.info(f"[{request_id}] New upload request received for file: {file.filename}")

    try:
        # Read audio bytes
        audio_bytes = await file.read()
        logger.info(f"[{request_id}] Audio bytes read successfully, length: {len(audio_bytes)}")

        # Process audio using facade
        try:
            transcript = await audio_processor.process_audio(audio_bytes, request_id)
        except Exception as e:
            logger.error(f"[{request_id}] Audio processing failed: {str(e)}")
            logger.debug(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Audio processing failed"
            )

        # Database operations (commented out in original code)
        # try:
        #     db = SessionLocal()
        #     visit = Visit(transcript=transcript, soap_note=soap_note)
        #     db.add(visit)
        #     db.commit()
        #     logger.info(f"[{request_id}] Visit record saved to database")
        # except Exception as e:
        #     logger.error(f"[{request_id}] Database operation failed: {str(e)}")
        #     logger.debug(traceback.format_exc())
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Database operation failed"
        #     )

        processing_time = time.time() - start_time
        logger.info(f"[{request_id}] Request completed in {processing_time:.2f} seconds")
        return {"transcript": transcript, "request_id": request_id}

    except HTTPException:
        # Re-raise HTTP exceptions as they're already formatted
        raise
    except Exception as e:
        # Catch any other unexpected exceptions
        logger.error(f"[{request_id}] Unexpected error in upload_audio: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during audio processing"
        )


@router.get("/notes/")
async def get_notes() -> Dict[str, Any]:
    """
    Generate notes from stored transcripts.

    Returns:
        Dict containing the generated notes

    Raises:
        HTTPException: If note generation fails
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    logger.info(f"[{request_id}] Notes generation request received")

    try:
        # Generate notes using notes generator
        try:
            notes, tokens = await notes_generator.generate_notes(request_id)
            if notes is None:
                return {"notes": None}

            processing_time = time.time() - start_time
            logger.info(f"[{request_id}] Request completed in {processing_time:.2f} seconds")
            return {"notes": notes, "request_id": request_id, "tokens_used": tokens}
        except Exception as e:
            logger.error(f"[{request_id}] Failed to generate notes: {str(e)}")
            logger.debug(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate notes"
            )

    except HTTPException:
        # Re-raise HTTP exceptions as they're already formatted
        raise
    except Exception as e:
        # Catch any other unexpected exceptions
        logger.error(f"[{request_id}] Unexpected error in get_notes: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during notes generation"
        )