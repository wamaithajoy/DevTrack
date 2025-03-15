from dotenv import load_dotenv
import os

load_dotenv()  # Loading environment variables

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
