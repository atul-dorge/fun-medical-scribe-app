# fun-medical-scribe-app
A medical scribe app which understands patient-healthcare provider conversations and generates SOAP notes


fun-medical-scribe-app/
├── app/
│ ├── api.py
│ ├── services/
│ │ └── transcription.py
│ ├── prompts.py
│ └── ... (other backend files)
├── static/
│ └── recorder.js
├── audio_uploads/ # Where audio files are stored
├── transcripts.txt # Where transcripts are stored
├── .env # Environment variables (not committed)
├── requirements.txt
└── README.md


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