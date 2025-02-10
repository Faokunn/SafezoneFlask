import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask
from database.base import Base, engine
from flasgger import Swagger
from flask_cors import CORS



from models.user_model import User
from models.sosalerts_model import SOSAlerter
from models.safezone_model import SafeZone
from models.safe_zone_status_history import SafeZoneStatusHistory
from models.profile_model import Profile
from models.notifications import Notification
from models.incidentreport_model import IncidentReport
from models.incident_report_status_history import IncidentReportStatusHistory 
from models.dangerzone_model import DangerZone
from models.contacts_model import ContactModel 
from models.circle_model import Circle
from models.groupmembers_model import GroupMember

from controllers.user_controller import user_controller
from controllers.contacts_controller import contact_controller 
from controllers.circle_controller import circle_controller
from controllers.incident_report_controller import incident_report_controller
from controllers.admin_incident_report_controller import admin_incident_report_controller
from controllers.admin_safe_zone_controller import admin_safe_zone_controller
from controllers.danger_zone_controller import danger_zone_controller
from controllers.safe_zone_controller import safe_zone_controller


load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)
# Connect to the database
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Register the blueprints
app.register_blueprint(user_controller, url_prefix='/user')
app.register_blueprint(contact_controller, url_prefix='/contacts')
app.register_blueprint(circle_controller, url_prefix='/circle')
app.register_blueprint(incident_report_controller, url_prefix='/incident-reports')
app.register_blueprint(admin_incident_report_controller, url_prefix='/admin/incident-reports')
app.register_blueprint(admin_safe_zone_controller, url_prefix='/admin/safe-zone')
app.register_blueprint(danger_zone_controller, url_prefix='/danger-zone')
app.register_blueprint(safe_zone_controller, url_prefix='/safe-zone')


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
