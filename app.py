import os
import json
import psycopg2
from dotenv import load_dotenv
from flask import Flask,request, jsonify
from database.base import Base, engine
from flasgger import Swagger
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, storage, firestore
import requests



from models.user_model import User
from models.sosalerts_model import SOSAlerter
from models.safezone_model import SafeZone
from models.safe_zone_status_history import SafeZoneStatusHistory
from models.notifications import Notification
from models.incidentreport_model import IncidentReport
from models.incident_report_status_history import IncidentReportStatusHistory 
from models.dangerzone_model import DangerZone
from models.contacts_model import ContactModel 
from models.circle_model import Circle
from models.groupmembers_model import GroupMember
from models.profile_model import Profile

from controllers.user_controller import user_controller
from controllers.contacts_controller import contact_controller 
from controllers.circle_controller import circle_controller
from controllers.incident_report_controller import incident_report_controller
from controllers.admin_analytics_controller import admin_analytics_controller
from controllers.admin_users_controller import admin_users_controller
from controllers.admin_incident_report_controller import admin_incident_report_controller
from controllers.admin_safe_zone_controller import admin_safe_zone_controller
from controllers.danger_zone_controller import danger_zone_controller
from controllers.safe_zone_controller import safe_zone_controller
from controllers.profile_controller import profile_controller
from controllers.groupmembers_controller import groupmember_controller
from controllers.notification_controller import notification_controller
from controllers.map_controller import map_controller


load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)
# Connect to the database
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

# Create tables in the database
Base.metadata.create_all(bind=engine)

FACEPP_KEY = os.getenv("FACEPP_KEY")
FACEPP_SECRET = os.getenv("FACEPP_SECRET")
THRESHOLD = float(os.getenv("THRESHOLD", 80))

# Register the blueprints
app.register_blueprint(user_controller, url_prefix='/user')
app.register_blueprint(contact_controller, url_prefix='/contacts')
app.register_blueprint(circle_controller, url_prefix='/circle')
app.register_blueprint(incident_report_controller, url_prefix='/incident-reports')
app.register_blueprint(admin_analytics_controller, url_prefix='/admin')
app.register_blueprint(admin_users_controller, url_prefix='/admin-users')
app.register_blueprint(admin_incident_report_controller, url_prefix='/admin/incident-reports')
app.register_blueprint(admin_safe_zone_controller, url_prefix='/admin/safe-zone')
app.register_blueprint(danger_zone_controller, url_prefix='/danger-zone')
app.register_blueprint(safe_zone_controller, url_prefix='/safe-zone')
app.register_blueprint(profile_controller, url_prefix='/profile')
app.register_blueprint(groupmember_controller, url_prefix='/groupmember')
app.register_blueprint(notification_controller, url_prefix='/notifications')
app.register_blueprint(map_controller, url_prefix='/map')


@app.route('/verify', methods=['POST'])
def verify_face():
    try:
        data = request.json
        id_image_base64 = data.get("id_image")
        selfie_base64 = data.get("selfie_image")

        if not id_image_base64 or not selfie_base64:
            return jsonify({"error": "Both images are required"}), 400

        response = requests.post(
            "https://api-us.faceplusplus.com/facepp/v3/compare",
            data={
                "api_key": FACEPP_KEY,
                "api_secret": FACEPP_SECRET,
                "image_base64_1": id_image_base64,
                "image_base64_2": selfie_base64
            }
        )

        result = response.json()
        confidence = result.get("confidence", 0)
        verified = confidence >= THRESHOLD

        return jsonify({
            "verified": verified,
            "confidence": confidence,
            "faceplusplus_result": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return 'Welcome to the Flask API!'

if __name__ == '__main__':
    app.run(debug=True)
