from flask import Blueprint, jsonify, request
from sqlalchemy.orm import sessionmaker
from database.base import engine
from services.safe_zone_services import (
    get_all_safe_zones_service,
    get_all_verified_safe_zones_service,
    get_safe_zone_by_id_service,
    get_safe_zones_by_status_service,
    get_safe_zones_by_user_id_service,
    get_status_history_service,
    create_safe_zone_service,
    update_safe_zone_service,
    delete_safe_zone_service
)

Session = sessionmaker(bind=engine)
session = Session()

safe_zone_controller = Blueprint('safe_zone_controller', __name__)

## GET

@safe_zone_controller.route("/safe-zones", methods=["GET"])
def get_safe_zones():
    try:
        return get_all_safe_zones_service(session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@safe_zone_controller.route("/verified-safe-zones", methods=["GET"])
def get_verified_safe_zones():
    try:
        return get_all_verified_safe_zones_service(session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@safe_zone_controller.route("/get-safe-zone/<int:safe_zone_id>", methods=["GET"])
def get_safe_zone_by_id(safe_zone_id):
    try:
        return get_safe_zone_by_id_service(safe_zone_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@safe_zone_controller.route('/status/<string:status>', methods=['GET']) 
def get_safe_zone_by_status(status):
    try:
        safezones = get_safe_zones_by_status_service(status, session)  
        return jsonify([safezone.to_dict() for safezone in safezones]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@safe_zone_controller.route('/user/<int:user_id>', methods=['GET']) 
def get_incidents_by_user(user_id):
    try:
        safezones = get_safe_zones_by_user_id_service(user_id, session)
        return jsonify([safezone.to_dict() for safezone in safezones]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@safe_zone_controller.route('/<int:safe_zone_id>/status_history', methods=['GET']) # TODO
def get_status_history(safe_zone_id):
    try:
        history = get_status_history_service(session, safe_zone_id)  
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
## CREATE

@safe_zone_controller.route('/safe-zone', methods=['POST']) 
def create_safe_zone():
    try:
        data = request.get_json()  
        result = create_safe_zone_service(data, session) 
        return jsonify(result), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
## UPDATE

@safe_zone_controller.route('/safe-zone/<int:safe_zone_id>', methods=['PUT'])
def update_safe_zone(safe_zone_id):
    try:
        data = request.get_json()
        result = update_safe_zone_service(safe_zone_id, data, session)
        
        if result is None:
            return jsonify({"message": "Safe Zone not found"}), 404
        
        return jsonify(result), 200  
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

## DELETE

@safe_zone_controller.route('/safe-zone/<int:safe_zone_id>', methods=['DELETE']) 
def delete_safe_zone(safe_zone_id):
    try:
        result = delete_safe_zone_service(safe_zone_id, session) 
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

