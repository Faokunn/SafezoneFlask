# database/base.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import json


load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)  

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class that all models will inherit
Base = declarative_base()

# Firebase Admin SDK Initialization
firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {'storageBucket': 'safezone-11724.firebasestorage.app'})
db = firestore.client()