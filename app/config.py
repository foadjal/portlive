# app/config.py
import os
from dotenv import load_dotenv




load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')  # à changer en prod
    UPLOAD_FOLDER = 'generated/'
