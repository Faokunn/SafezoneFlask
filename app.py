import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask
from database.base import Base, engine
from models.user_model import User
from models.sosalerts_model import SOSAlerter
from models.safezone_model import SafeZone
from models.profile_model import Profile
from models.notifications import Notification
from models.incidentreport_model import IncidentReport
from models.incident_report_status_history import IncidentReportStatusHistory 
from models.dangerzone_model import DangerZone
from models.contacts_model import ContactModel 
from models.circle_model import Circle
from models.association_tables import group_members

load_dotenv()

app = Flask(__name__)
Base.metadata.create_all(bind=engine)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.route('/')
def home():
    return 'Welcome to the Flask API!'
