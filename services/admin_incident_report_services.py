from flask import jsonify, abort
from sqlalchemy.orm import sessionmaker
from database.base import engine
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError
from models.incidentreport_model import IncidentReport
from models.incident_report_status_history import IncidentReportStatusHistory
from models.dangerzone_model import DangerZone

Session = sessionmaker(bind=engine)

def add_status_history(session, incident_report_id, status, remarks=None):
    status_history = IncidentReportStatusHistory(
        incident_report_id=incident_report_id,
        status=status,
        timestamp=datetime.now(ZoneInfo("Asia/Manila")),
        remarks=remarks,
    )
    session.add(status_history)

def verify_incident_report_service(incident_id, session):
    try:
        incident_report = session.query(IncidentReport).filter_by(id=incident_id).first()
        if not incident_report:
            abort(404, description="Incident report not found")

        incident_report.status = "verified"
        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
        session.add(incident_report)

        add_status_history(session, incident_report_id=incident_id, status="verified", remarks="Incident report verified.")

        danger_zone_data = None
        if incident_report.danger_zone_id:
            danger_zone = session.query(DangerZone).filter_by(id=incident_report.danger_zone_id).first()
            if danger_zone:
                danger_zone.is_verified = True
                danger_zone.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
                session.add(danger_zone)

                danger_zone_data = {
                    "id": danger_zone.id,
                    "is_verified": danger_zone.is_verified,
                    "updated_at": danger_zone.updated_at.isoformat(),
                }

        session.commit()

        return jsonify({
            "message": f"Incident report {incident_id} verified.",
            "incident_report": {
                "id": incident_report.id,
                "status": incident_report.status,
                "updated_at": incident_report.updated_at.isoformat(),
            },
            "danger_zone": danger_zone_data,
        }), 200

    except IntegrityError as e:
        session.rollback()
        abort(400, description=f"Error verifying incident report: {str(e)}")
    except Exception as e:
        session.rollback()
        abort(500, description=f"An error occurred: {str(e)}")

def reject_incident_report_service(incident_id, session):
    try:
        incident_report = session.query(IncidentReport).filter_by(id=incident_id).first()
        if not incident_report:
            abort(404, description="Incident report not found")

        incident_report.status = "rejected"
        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
        session.add(incident_report)

        add_status_history(session, incident_report_id=incident_id, status="rejected", remarks="Incident report rejected.")

        session.commit()

        return jsonify({
            "message": f"Incident report {incident_id} rejected.",
            "incident_report": {
                "id": incident_report.id,
                "status": incident_report.status,
                "updated_at": incident_report.updated_at.isoformat(),
            }
        }), 200

    except IntegrityError as e:
        session.rollback()
        abort(400, description=f"Error rejecting incident report: {str(e)}")
    except Exception as e:
        session.rollback()
        abort(500, description=f"An error occurred: {str(e)}")

def under_review_incident_report_service(incident_id, session):
    try:
        incident_report = session.query(IncidentReport).filter_by(id=incident_id).first()
        if not incident_report:
            abort(404, description="Incident report not found")

        incident_report.status = "under review"
        incident_report.updated_at = datetime.now(ZoneInfo("Asia/Manila"))
        session.add(incident_report)

        add_status_history(session, incident_report_id=incident_id, status="under review", remarks="Incident report is under review.")

        session.commit()

        return jsonify({
            "message": f"Incident report {incident_id} is under review.",
            "incident_report": {
                "id": incident_report.id,
                "status": incident_report.status,
                "updated_at": incident_report.updated_at.isoformat(),
            }
        }), 200

    except IntegrityError as e:
        session.rollback()
        abort(400, description=f"Error updating incident report: {str(e)}")
    except Exception as e:
        session.rollback()
        abort(500, description=f"An error occurred: {str(e)}")