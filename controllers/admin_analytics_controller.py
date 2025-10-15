from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.base import engine
from services.admin_analytics_services import get_all_safe_zones_service, get_all_users_safe_zones_incidents_service, get_users_with_incidents_and_safe_zones_service, get_users_with_incidents_service, get_all_incidents, get_users_with_safe_zones_service
from sqlalchemy.orm import joinedload
Session = sessionmaker(bind=engine)
session = Session()

admin_analytics_controller = Blueprint('admin_analytics_controller', __name__)

## GET DATA

@admin_analytics_controller.route('/all-data', methods=['GET'])
def get_all_data():
    try:
        all_data = get_all_users_safe_zones_incidents_service(session)
        return jsonify(all_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


## GET SAFEZONES AND INCIDENTS

@admin_analytics_controller.route('/users-with-data', methods=['GET'])
def get_users_with_data():
    try:
        users_with_data = get_users_with_incidents_and_safe_zones_service(session)
        return jsonify(users_with_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


## GET INCIDENTS

@admin_analytics_controller.route('/incidents', methods=['GET']) 
def get_incidents():
    try:
        incidents = get_all_incidents(session) 
        return jsonify(incidents), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@admin_analytics_controller.route('/users-with-incidents', methods=['GET'])
def get_users_with_incidents():
    try:
        users_with_incidents = get_users_with_incidents_service(session)
        return jsonify(users_with_incidents), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

## GET SAFEZONES

@admin_analytics_controller.route("/safe-zones", methods=["GET"])
def get_safe_zones():
    try:
        return get_all_safe_zones_service(session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@admin_analytics_controller.route('/users-with-safezones', methods=['GET'])
def get_users_with_safe_zones():
    try:
        users_with_safezones = get_users_with_safe_zones_service(session)
        return jsonify(users_with_safezones), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
