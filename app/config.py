from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

class Settings:
    MONGO_URL: str = os.getenv("MONGO_URL")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

settings = Settings()
