# fun-medical-scribe-app
A medical scribe app which understands patient-healthcare provider conversations and generates SOAP notes

## 📐 Architecture Overview

### 🖼️ Frontend
**Files:** `static/recorder.js`, HTML  
- Provides a web UI to:
  - Record audio  
  - Upload audio to the backend  
  - Display transcripts and SOAP notes  
- Sends audio data via HTTP requests  
- Fetches and renders transcripts and SOAP notes

---

### ⚙️ Backend (FastAPI in `app/`)

#### 🔹 API Layer (`app/api.py`)
- Exposes endpoints to:
  - Upload audio  
  - Retrieve transcripts  
  - Generate SOAP notes  
- Handles file-based storage (no database)

#### 🔹 Transcription Service (`app/services/transcription.py`)
- Uses **Deepgram API** to:
  - Transcribe audio  
  - Perform speaker diarization  
- Returns structured transcript data

#### 🔹 LLM Service (`app/services/llm.py`)
- Sends transcripts to **OpenAI API**  
- Generates SOAP notes using prompt templates

#### 🔹 Prompts (`app/prompts.py`)
- Stores and manages prompt templates used by the LLM service

---

## 💾 Storage

- **Audio Files:**  
  - Stored in `audio_uploads/` with UUID filenames  
- **Transcripts:**  
  - Appended line-by-line in `transcripts.txt`

---

## 🔐 Configuration

- API keys and secrets are managed via environment variables  
- Loaded automatically from a `.env` file

---


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/atul-dorge/fun-medical-scribe-app
cd fun-medical-scribe-app
```

### 2. Create and Activate a Virtual Environment Using Python Version 3.9.20 (Recommended)

```bash
conda create --name medic_scribe_v3 python=3.9.20
conda activate medic_scribe_v3
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in app/.env with the following content:

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Replace the values with your actual API keys.

### 5. Run the Backend

Navigate to directory : /fun-medical-scribe-app/app
Run uvicorn main:app --reload

## Usage

1. Open the web app in your browser.
2. Click **Start Recording** to begin recording audio.
3. Click **Stop Recording** to stop and upload the audio.
4. Click **Get Transcript** to fetch the latest transcript.
5. Click **Generate Notes** (or similar) to generate SOAP notes from the transcript.

---

## File Storage

- **Audio files** are saved in the `audio_uploads/` directory with unique UUID filenames.
- **Transcripts** are appended to `transcripts.txt`, one per line.

---

## API Endpoints

- `POST /upload/`  
  Uploads audio, saves it, transcribes it, and stores the transcript.

- `GET /notes/`  
  Returns generated SOAP notes based on stored transcripts.

- (You may have additional endpoints for fetching transcripts, etc.)

---

## Requirements

- See `requirements.txt` for Python dependencies

---

## Security

**Never commit your `.env` file or API keys to version control.**  

