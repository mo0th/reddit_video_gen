import os
from os import path
from dotenv import load_dotenv

# Load environment variables from .env
dotenv_path = path.join(path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
