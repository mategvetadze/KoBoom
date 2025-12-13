import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "sqlite:///./app/data/problems.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")

DIFFICULTY_MODEL_PATH = "app/data/models/difficulty_model.h5"
HINT_TIMING_MODEL_PATH = "app/data/models/hint_timing_model.h5"
SYNTHETIC_DATA_PATH = "app/data/training/synthetic_data.pkl"
