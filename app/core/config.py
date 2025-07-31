from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    MONGODB_URI = os.getenv("MONGODB", "mongodb://localhost:27017/default")

settings = Settings()
