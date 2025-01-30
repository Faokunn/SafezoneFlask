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
from flasgger import Swagger
from models.groupmembers_model import GroupMember

from controllers.user_controller import user_controller
from controllers.contacts_controller import contact_controller  # Import contacts_controller

load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)

# Connect to the database
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Register the blueprints
app.register_blueprint(user_controller, url_prefix='/user')
app.register_blueprint(contact_controller, url_prefix='/contacts')
app.register_blueprint(circle_controller, url_prefix='/circle')  # Register contacts controller
app.register_blueprint(incident_report_controller, url_prefix='/incident-reports')

app.config['SWAGGER'] = {
    'title': 'Flask Incident Reports API',
    'uiversion': 3,
    'definitions': {
        'IncidentReport': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer'},
                'danger_zone_id': {'type': 'integer'},
                'user_id': {'type': 'integer'},
                'description': {'type': 'string'},
                'report_date': {'type': 'string', 'format': 'date'},
                'report_time': {'type': 'string', 'format': 'time'},
                'images': {'type': 'array', 'items': {'type': 'string'}},
                'status': {'type': 'string'},
                'report_timestamp': {'type': 'string', 'format': 'date-time'},
                'updated_at': {'type': 'string', 'format': 'date-time'},
            }
        }
    }
}


@app.route('/')
def home():
    return 'Welcome to the Flask API!'

if __name__ == '__main__':
    app.run(debug=True)
