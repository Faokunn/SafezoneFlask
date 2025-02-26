from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.base import engine
from services.admin_safe_zone_services import (
    verify_safe_zone_service,
    reject_safe_zone_service,
    under_review_safe_zone_service
)

Session = sessionmaker(bind=engine)
session = Session()

admin_safe_zone_controller = Blueprint('admin_safe_zone_controller', __name__)

## ADMIN VERIFICATION OF SAFEZONES

@admin_safe_zone_controller.route("/verify-safezone/<int:safezone_id>", methods=["PUT"])
def verify_safe_zone(safezone_id):
    try:
        return verify_safe_zone_service(safezone_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_safe_zone_controller.route("/reject-safezone/<int:safezone_id>", methods=["PUT"])
def reject_safe_zone(safezone_id):
    try:
        return reject_safe_zone_service(safezone_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_safe_zone_controller.route("/review-safezone/<int:safezone_id>", methods=["PUT"])
def review_safe_zone(safezone_id):
    try:
        return under_review_safe_zone_service(safezone_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
