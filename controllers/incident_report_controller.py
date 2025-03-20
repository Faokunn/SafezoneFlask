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
    upload_images_to_firebase
)

Session = sessionmaker(bind=engine)
session = Session()

incident_report_controller = Blueprint('incident_report_controller', __name__)

@incident_report_controller.route('/upload', methods=['POST'])
def upload():
    try:
        if 'images' not in request.files:
            return jsonify({"error": "No images provided"}), 400

        files = request.files.getlist('images')  # Get multiple image files
        uploaded_urls = upload_images_to_firebase(files)  # Call the service function

        return jsonify({
            "message": "Images uploaded successfully",
            "uploaded_urls": uploaded_urls
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incidents', methods=['GET']) 
def get_incidents():
    try:
        incidents = get_all_incidents(session) 
        return jsonify(incidents), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incident/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    try:
        incident = get_incident_report_by_id_service(incident_id, session)  
        if not incident:
            return jsonify({"message": "Incident not found"}), 404
        return jsonify(incident.to_dict()), 200  
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incidents/danger_zone/<int:danger_zone_id>', methods=['GET']) 
def get_incidents_by_danger_zone(danger_zone_id):
    try:
        incidents = get_incident_report_by_danger_zone_id_service(danger_zone_id, session)  
        return jsonify([incident.to_dict() for incident in incidents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incidents/status/<string:status>', methods=['GET']) 
def get_incidents_by_status(status):
    try:
        incidents = get_incident_report_by_status_service(status, session)  
        return jsonify([incident.to_dict() for incident in incidents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incidents/user/<int:user_id>', methods=['GET']) 
def get_incidents_by_user(user_id):
    try:
        incidents = get_incident_report_by_user_id_service(user_id, session)
        return jsonify([incident.to_dict() for incident in incidents]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @incident_report_controller.route('/incident', methods=['POST']) 
# def create_incident():
#     try:
#         data = request.get_json()  
#         result = create_incident_report_service(data, session) 
#         return jsonify(result), 200 
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incident', methods=['POST']) 
def create_incident():
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = {
                'user_id': int(request.form.get('user_id')),
                'description': request.form.get('description'),
                'report_date': request.form.get('report_date'),
                'report_time': request.form.get('report_time'),
                'report_timestamp': request.form.get('report_timestamp'),
                'latitude': float(request.form.get('latitude')),
                'longitude': float(request.form.get('longitude')),
                'radius': float(request.form.get('radius')),
                'name': request.form.get('name')
            }
            danger_zone_id = request.form.get('danger_zone_id')
            if danger_zone_id:
                data['danger_zone_id'] = int(danger_zone_id)
                
            images = request.files.getlist('images')
            data['images'] = images
        else:
            data = request.get_json()
            data['images'] = []  
            
        result = create_incident_report_service(data, session) 
        return jsonify(result), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#### testing in form data

# @incident_report_controller.route('/incident', methods=['POST']) 
# def create_incident():
#     try:
#         # Extract form data
#         data = request.form.to_dict()

#         # Convert numeric values properly
#         data['user_id'] = int(data['user_id'])
#         data['latitude'] = float(data['latitude'])
#         data['longitude'] = float(data['longitude'])
#         data['radius'] = float(data['radius'])

#         # Handle images
#         if 'images' in request.files:
#             files = request.files.getlist('images')  # Get all uploaded images
#             uploaded_image_urls = upload_images_to_firebase(files)  # Upload images
#             data['images'] = uploaded_image_urls  # Store image URLs in `data`

#         # Fix `report_timestamp` (combine date & time if needed)
#         if 'report_date' in data and 'report_time' in data:
#             data['report_timestamp'] = f"{data['report_date']}T{data['report_time']}:00Z"

#         # Call the service function to process the report
#         result = create_incident_report_service(data, session)
#         return jsonify(result), 200  

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incident/<int:incident_id>', methods=['PUT'])
def update_incident(incident_id):
    try:
        data = request.get_json()
        result = update_incident_report_service(incident_id, data, session)
        
        if result is None:
            return jsonify({"message": "Incident not found"}), 404
        
        return jsonify(result), 200  
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incident/<int:incident_id>', methods=['DELETE']) 
def delete_incident(incident_id):
    try:
        result = delete_incident_report_service(incident_id, session) 
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@incident_report_controller.route('/incident/<int:incident_id>/status_history', methods=['GET']) # TODO
def get_status_history(incident_id):
    try:
        history = get_status_history_service(session, incident_id)  
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
