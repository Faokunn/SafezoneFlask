from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.base import engine
from services.incident_report_services import (
    get_all_incidents,
    get_incident_report_by_id_service,
    get_incident_report_by_danger_zone_id_service,
    get_incident_report_by_status_service,
    get_incident_report_by_user_id_service,
    create_incident_report_service,
    update_incident_report_service,
    delete_incident_report_service,
    get_status_history_service,
)

# Database connection and session
Session = sessionmaker(bind=engine)
session = Session()

incident_report_controller = Blueprint('incident_report_controller', __name__)

# Route to get all incidents
@incident_report_controller.route('/incidents', methods=['GET'])
def get_incidents():
    try:
        incidents = get_all_incidents(session)  # Call the service
        return jsonify([incident.to_dict() for incident in incidents]), 200  # Convert incidents to a dict if necessary
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get an incident by its ID
@incident_report_controller.route('/incident/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    try:
        incident = get_incident_report_by_id_service(incident_id, session)  # Call the service
        if not incident:
            return jsonify({"message": "Incident not found"}), 404
        return jsonify(incident.to_dict()), 200  # Convert incident to a dict if necessary
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get incidents by danger zone ID
@incident_report_controller.route('/incidents/danger_zone/<int:danger_zone_id>', methods=['GET'])
def get_incidents_by_danger_zone(danger_zone_id):
    try:
        incidents = get_incident_report_by_danger_zone_id_service(danger_zone_id, session)  # Call the service
        return jsonify([incident.to_dict() for incident in incidents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get incidents by status
@incident_report_controller.route('/incidents/status/<string:status>', methods=['GET'])
def get_incidents_by_status(status):
    try:
        incidents = get_incident_report_by_status_service(status, session)  # Call the service
        return jsonify([incident.to_dict() for incident in incidents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get incidents by user ID
@incident_report_controller.route('/incidents/user/<int:user_id>', methods=['GET'])
def get_incidents_by_user(user_id):
    try:
        incidents = get_incident_report_by_user_id_service(user_id, session)  # Call the service
        return jsonify([incident.to_dict() for incident in incidents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to create an incident report
@incident_report_controller.route('/incident', methods=['POST'])
def create_incident():
    try:
        data = request.get_json()  # Get data from the request
        result = create_incident_report_service(data, session)  # Call the service
        return jsonify(result), 200  # Return the result from the service
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update an incident report
@incident_report_controller.route('/incident/<int:incident_id>', methods=['PUT'])
def update_incident(incident_id):
    try:
        data = request.get_json()  # Get data from the request
        result = update_incident_report_service(incident_id, data, session)  # Call the service
        if result is None:
            return jsonify({"message": "Incident not found"}), 404
        return jsonify(result), 200  # Return the result from the service
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete an incident report
@incident_report_controller.route('/incident/<int:incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    try:
        result = delete_incident_report_service(incident_id, session)  # Call the service
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get the status history of an incident report
@incident_report_controller.route('/incident/<int:incident_id>/status_history', methods=['GET'])
def get_status_history(incident_id):
    try:
        history = get_status_history_service(session, incident_id)  # Call the service
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
