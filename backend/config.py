import os

from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# Language Settings
SUPPORTED_LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "ka": "Georgian (ქართული)",
    "sk": "Slovak (Slovenčina)",
    "sl": "Slovenian (Slovenščina)",
    "lv": "Latvian (Latviešu)",
}


# Service Configuration
WHISPER_CONFIG = {"model": "whisper-1", "response_format": "verbose_json"}

ASSEMBLYAI_CONFIG = {
    "model": "best",
    "language_detection": True,
    "speaker_labels": True,
}

# Translation Settings
TRANSLATION_CONFIG = {
    "ka": {
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 2000,
        "system_prompt": "You are a professional Georgian to English translator. Translate the following text accurately, preserving speaker tone and meaning.",
    },
    "sk": {
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 2000,
        "system_prompt": "You are a professional Slovak to English translator. Translate the following text clearly and accurately.",
    },
    "sl": {
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 2000,
        "system_prompt": "You are a professional Slovenian to English translator. Translate the following text clearly and accurately.",
    },
    "lv": {
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 2000,
        "system_prompt": "You are a professional Latvian to English translator. Translate the following text clearly and accurately.",
    },
}


# File Storage
DATA_DIR = "backend/data"
TEMP_DIR = "backend/temp"
