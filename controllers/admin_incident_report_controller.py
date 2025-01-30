from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.base import engine
from services.admin_incident_report_services import verify_incident_report_service
from services.admin_incident_report_services import (
    verify_incident_report_service,
    reject_incident_report_service,
    under_review_incident_report_service
)

Session = sessionmaker(bind=engine)
session = Session()

admin_incident_report_controller = Blueprint('admin_incident_report_controller', __name__)

@admin_incident_report_controller.route("/verify-report/<int:incident_id>", methods=["PUT"])
def verify_incident_report(incident_id):
    try:
        return verify_incident_report_service(incident_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_incident_report_controller.route("/reject-report/<int:incident_id>", methods=["PUT"])
def reject_incident_report(incident_id):
    try:
        return reject_incident_report_service(incident_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_incident_report_controller.route("/review-report/<int:incident_id>", methods=["PUT"])
def review_incident_report(incident_id):
    try:
        return under_review_incident_report_service(incident_id, session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
