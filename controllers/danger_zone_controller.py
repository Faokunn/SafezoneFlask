from flask import Blueprint, jsonify
from sqlalchemy.orm import sessionmaker
from database.base import engine
from services.danger_zone_services import (
    get_all_danger_zones_service,
    get_danger_zone_by_id_service
)

Session = sessionmaker(bind=engine)
session = Session()

danger_zone_controller = Blueprint('danger_zone_controller', __name__)

@danger_zone_controller.route("/danger-zones", methods=["GET"])
def get_danger_zones():
    try:
        return get_all_danger_zones_service(session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@danger_zone_controller.route("/get-danger-zone/<int:danger_zone_id>", methods=["GET"])
def get_danger_zone_by_id(danger_zone_id):
    try:
        return get_danger_zone_by_id_service(danger_zone_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
