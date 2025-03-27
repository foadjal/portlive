import os
from dotenv import load_dotenv

# Charger les variables d’environnement depuis le fichier .env
load_dotenv()

# Base directory du projet
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Chemin vers la base de données SQLite
DATABASE_FILE = os.path.join(BASE_DIR, '..', 'database', 'vessel_flags.db')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')  # À changer en prod
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'generated')
