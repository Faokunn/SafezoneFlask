from models.dangerzone_model import DangerZone
from models.incident_report_status_history import IncidentReportStatusHistory
from models.incidentreport_model import IncidentReport
from sqlalchemy.orm import sessionmaker
from database.base import engine
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError
from models.user_model import User
from flask import abort
from firebase_admin import storage
import pytz

Session = sessionmaker(bind=engine)


def add_status_history(session, incident_report_id, status, remarks=None):
    status_history = IncidentReportStatusHistory(
        incident_report_id=incident_report_id,
        status=status,
        timestamp=datetime.now(),
        remarks=remarks,
    )
    session.add(status_history)

def upload_images_to_firebase(files):
    uploaded_urls = []
    
    if not files:
        return uploaded_urls 

    bucket = storage.bucket() 
    
    for file in files:
        filename = file.filename.lower()
        if not filename.endswith((".jpg", ".jpeg", ".png")):
            abort(400, description=f"File {filename} must be an image")
        
        blob = bucket.blob(f"incident_images/{filename}")  
        blob.upload_from_file(file, content_type=file.mimetype)
        blob.make_public()  
        uploaded_urls.append(blob.public_url)

    return uploaded_urls


# def upload_images_to_firebase(files):
#     uploaded_urls = []
    
#     if not files:
#         return uploaded_urls  # Return empty list if no images provided

#     bucket = storage.bucket()  # Ensure Firebase initialized properly
    
#     for file in files:
#         if not hasattr(file, 'filename'):  # Ensure it's a file object
#             continue

#         filename = file.filename.lower()
#         if not filename.endswith((".jpg", ".jpeg", ".png")):
#             abort(400, description=f"File {filename} must be an image")
        
#         blob = bucket.blob(f"incident_images/{filename}")  
#         blob.upload_from_file(file, content_type=file.mimetype)
#         blob.make_public()  
#         uploaded_urls.append(blob.public_url)  # Store Firebase URL
        
#     return uploaded_urls

# def parse_report_timestamp(timestamp):
#     try:
#         if isinstance(timestamp, str):
#             return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Manila"))
#         return timestamp.astimezone(ZoneInfo("Asia/Manila"))
#     except Exception as e:
#         abort(400, description=f"Invalid report_timestamp: {str(e)}")

def parse_report_timestamp(timestamp):
    try:
        manila_tz = pytz.timezone("Asia/Manila")

        if isinstance(timestamp, str):
            timestamp = timestamp.strip() 
            if "T" in timestamp:  
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:  
                dt = datetime.strptime(timestamp, "%H:%M:%S")  
        else:
            dt = timestamp  

        return dt.astimezone(manila_tz)
    except Exception as e:
        abort(400, description=f"Invalid report_timestamp: {str(e)}")

def get_or_create_danger_zone(session, latitude, longitude, radius, name, danger_zone_id=None):
    if danger_zone_id:
        danger_zone = session.query(DangerZone).filter_by(id=danger_zone_id).first()
        if danger_zone:
            return danger_zone 
    
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
        return [incident.to_dict() for incident in incidents]
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

# def create_incident_report_service(data, session):
#     try:
#         user = session.query(User).filter_by(id=data['user_id']).first()
#         if not user:
#             abort(404, description="User not found") 

#         report_timestamp = parse_report_timestamp(data['report_timestamp'])

#         danger_zone = get_or_create_danger_zone(
#             session, 
#             data['latitude'], 
#             data['longitude'], 
#             data['radius'], 
#             data['name'], 
#             danger_zone_id=data.get('danger_zone_id')
#         )

#         current_time = datetime.now()
#         incident_report = IncidentReport(
#             user_id=data['user_id'],
#             danger_zone_id=danger_zone.id,
#             description=data['description'],
#             report_date=data['report_date'],
#             report_time=data['report_time'],
#             images=data.get('images', []), 
#             report_timestamp=report_timestamp,
#             updated_at=current_time
#         )

#         session.add(incident_report)
#         session.flush()  

#         add_status_history(session, incident_report_id=incident_report.id, status="pending", remarks="Incident report pending.")

#         session.commit()

#         return {
#             "message": "Incident report created successfully",
#             "incident_report_id": incident_report.id,
#             "is_verified": danger_zone.is_verified
#         }, 200

#     except IntegrityError as e:
#         session.rollback()
#         abort(400, description=f"Error creating incident report: {str(e)}")  
#     except Exception as e:
#         session.rollback()
#         abort(500, description=f"An error occurred: {str(e)}")  



def create_incident_report_service(data, session):
    try:
        user = session.query(User).filter_by(id=data['user_id']).first()
        if not user:
            abort(404, description="User not found") 

        report_timestamp = parse_report_timestamp(data['report_timestamp'])

        # Find or create the danger zone
        danger_zone = get_or_create_danger_zone(
            session, 
            data['latitude'], 
            data['longitude'], 
            data['radius'], 
            data['name'], 
            danger_zone_id=data.get('danger_zone_id')
        )

        uploaded_image_urls = upload_images_to_firebase(data.get('images', []))

        current_time = datetime.now()
        incident_report = IncidentReport(
            user_id=data['user_id'],
            danger_zone_id=danger_zone.id,
            description=data['description'],
            report_date=data['report_date'],
            report_time=data['report_time'],
            images=uploaded_image_urls, 
            report_timestamp=report_timestamp,
            updated_at=current_time
        )

        add_status_history(session, incident_report_id=incident_report.id, status="pending", remarks="Incident report pending.")

        session.add(incident_report)
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            abort(400, description=f"Error creating incident report: {str(e)}")  

        return {
            "message": "Incident report created successfully",
            "incident_report_id": incident_report.id,
            "uploaded_images": uploaded_image_urls,  # Return uploaded images
            "is_verified": danger_zone.is_verified
        }, 200

    except Exception as e:
        session.rollback()
        abort(500, description=f"An error occurred: {str(e)}")  

    
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

        new_latitude = data.get('latitude')
        new_longitude = data.get('longitude')
        new_radius = data.get('radius') 
        new_name = data.get('name')  

        if new_latitude is not None and new_longitude is not None:
            existing_danger_zone = session.query(DangerZone).filter_by(latitude=new_latitude, longitude=new_longitude).first()

            if existing_danger_zone:
                incident.danger_zone_id = existing_danger_zone.id
            else:
                new_danger_zone = DangerZone(
                    latitude=new_latitude,
                    longitude=new_longitude,
                    radius=new_radius if new_radius else 100,  
                    name=new_name if new_name else "Unknown",
                    is_verified=False
                )
                session.add(new_danger_zone)
                session.commit() 
                incident.danger_zone_id = new_danger_zone.id  

        session.commit()

        return {
            "message": "Incident report updated successfully",
            "incident_report": incident.to_dict()
        }
    except Exception as e:
        session.rollback()
        return {"error": str(e)}

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
        status_history = (
            session.query(IncidentReportStatusHistory)
            .filter(IncidentReportStatusHistory.incident_report_id == incident_id)
            .order_by(IncidentReportStatusHistory.timestamp.desc())  # Sort by latest first
            .all()
        )
        
        return [status.to_dict() for status in status_history]
    
    except Exception as e:
        return {"error": str(e)}
