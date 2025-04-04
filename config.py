import os

class Config:
    # Configuration de la base de données SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///smart_aqua_farm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'votre_clé_secrète'  # Utilisez une clé secrète plus sécurisée en production