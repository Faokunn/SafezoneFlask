from models.dangerzone_model import DangerZone
from models.incidentreport_model import IncidentReport
from sqlalchemy.orm import sessionmaker
from database.base import engine
from datetime import datetime
from flask import HTTPException
from zoneinfo import ZoneInfo

# Database connection and session
Session = sessionmaker(bind=engine)

def handle_exception(e: Exception):
    """Handle exceptions by re-raising HTTPExceptions."""
    if isinstance(e, HTTPException):
        raise e
    raise HTTPException(status_code=500, detail=str(e))

def parse_report_timestamp(timestamp):
    """Parse the report timestamp and convert it to Asia/Manila timezone."""
    try:
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Manila"))
        return timestamp.astimezone(ZoneInfo("Asia/Manila"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid report_timestamp: {str(e)}")

def get_or_create_danger_zone(session, latitude, longitude, radius, name, danger_zone_id=None):
    """Fetch or create a Danger Zone based on the data."""
    if danger_zone_id:
        danger_zone = session.query(DangerZone).filter_by(id=danger_zone_id).first()
        if not danger_zone:
            raise HTTPException(status_code=404, detail="Danger Zone not found.")
    else:
        danger_zone = session.query(DangerZone).filter(
            DangerZone.latitude == latitude, DangerZone.longitude == longitude
        ).first()

        if not danger_zone:
            danger_zone = DangerZone(
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                name=name,
                is_verified=False
            )
            session.add(danger_zone)
            session.commit()

    return danger_zone

def get_all_incidents(session):
    try:
        incidents = session.query(IncidentReport).all()
        return incidents
    except Exception as e:
        return str(e)

def get_incident_report_by_id_service(incident_id, session):
    try:
        incident = session.query(IncidentReport).filter_by(id=incident_id).first()
        if not incident:
            return None
        return incident
    except Exception as e:
        return str(e)

def get_incident_report_by_danger_zone_id_service(danger_zone_id, session):
    try:
        incidents = session.query(IncidentReport).filter_by(danger_zone_id=danger_zone_id).all()
        return incidents
    except Exception as e:
        return str(e)

def get_incident_report_by_status_service(status, session):
    try:
        incidents = session.query(IncidentReport).filter_by(status=status).all()
        return incidents
    except Exception as e:
        return str(e)

def get_incident_report_by_user_id_service(user_id, session):
    try:
        incidents = session.query(IncidentReport).filter_by(user_id=user_id).all()
        return incidents
    except Exception as e:
        return str(e)

def create_incident_report_service(data, session):
    try:
        incident = IncidentReport(
            user_id=data['user_id'],
            danger_zone_id=data['danger_zone_id'],
            description=data['description'],
            report_date=data['report_date'],
            report_time=data['report_time'],
            images=data['images'],
            report_timestamp=datetime.now(),
        )
        session.add(incident)
        session.commit()
        return {"message": "Incident report created successfully", "incident_report_id": incident.id}
    except Exception as e:
        session.rollback()
        return str(e)

def update_incident_report_service(incident_id, data, session):
    try:
        incident = session.query(IncidentReport).filter_by(id=incident_id).first()
        if not incident:
            return None
        incident.description = data.get('description', incident.description)
        incident.report_date = data.get('report_date', incident.report_date)
        incident.report_time = data.get('report_time', incident.report_time)
        incident.status = data.get('status', incident.status)
        incident.images = data.get('images', incident.images)
        incident.danger_zone_id = data.get('danger_zone_id', incident.danger_zone_id)
        session.commit()
        return {"message": "Incident report updated successfully", "incident_report": incident}
    except Exception as e:
        session.rollback()
        return str(e)

def delete_incident_report_service(incident_id, session):
    try:
        incident = session.query(IncidentReport).filter_by(id=incident_id).first()
        if not incident:
            return {"message": "Incident report not found"}
        session.delete(incident)
        session.commit()
        return {"message": f"Incident report {incident_id} deleted successfully"}
    except Exception as e:
        session.rollback()
        return str(e)

def get_status_history_service(session, incident_id):
    try:
        # Add logic to fetch incident status history
        return []
    except Exception as e:
        return str(e)
