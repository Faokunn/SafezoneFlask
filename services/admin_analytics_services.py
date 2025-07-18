from flask import jsonify, abort
from sqlalchemy.orm import sessionmaker
from database.base import engine
from models.incidentreport_model import IncidentReport
from models.safezone_model import SafeZone
from models.user_model import User

Session = sessionmaker(bind=engine)

## DATA

def get_all_users_safe_zones_incidents_service(session):
    try:
        users = session.query(User).all()
        incidents = session.query(IncidentReport).all()
        safe_zones = session.query(SafeZone).all()

        result = {
            "users": [user.to_dict() for user in users],
            "incident_reports": [incident.to_dict() for incident in incidents],
            "safe_zones": [safe_zone.to_dict() for safe_zone in safe_zones]
        }

        return result
    except Exception as e:
        return str(e)
    

## SAFEZONES AND INCIDENTS

def get_users_with_incidents_and_safe_zones_service(session):
    try:
        users = session.query(User).all()
        result = []

        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username, 
                "email": user.email,
                "profile_picture_url": user.profile.profile_picture_url if user.profile else None, 
                "incident_reports": [incident.to_dict() for incident in user.incident_reports],
                "safe_zones": [safe_zone.to_dict() for safe_zone in user.safe_zones]
            }
            result.append(user_data)

        return result
    except Exception as e:
        return str(e)

## INCIDENTS

def get_all_incidents(session):
    try:
        incidents = session.query(IncidentReport).all()
        return [incident.to_dict() for incident in incidents]
    except Exception as e:
        return str(e)

def get_users_with_incidents_service(session):
    try:
        users = session.query(User).all()
        result = []
        
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,  # Assuming `name` is a field in your User model
                "email": user.email,  # Assuming `email` is a field in your User model
                "profile_picture_url": user.profile.profile_picture_url if user.profile else None, 
                "incident_reports": [incident.to_dict() for incident in user.incident_reports]
            }
            result.append(user_data)

        return result
    except Exception as e:
        return str(e)


## SAFEZONES

def get_all_safe_zones_service(session):
    try:
        safe_zones = session.query(SafeZone).all()

        safe_zones_data = [safe_zone.to_dict() for safe_zone in safe_zones]

        return jsonify(safe_zones_data), 200

    except Exception as e:
        abort(500, description=f"Error retrieving safe zones: {str(e)}")

def get_users_with_safe_zones_service(session):
    try:
        users = session.query(User).all()
        result = []
        
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,  # Assuming `name` is a field in your User model
                "email": user.email,  # Assuming `email` is a field in your User model
                "profile_picture_url": user.profile.profile_picture_url if user.profile else None, 
                "safe_zones": [safe_zone.to_dict() for safe_zone in user.safe_zones]
            }
            result.append(user_data)

        return result
    except Exception as e:
        return str(e)


