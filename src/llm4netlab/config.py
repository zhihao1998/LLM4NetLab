import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getenv("BASE_DIR")
RESULTS_DIR = os.getenv("RESULTS_DIR")