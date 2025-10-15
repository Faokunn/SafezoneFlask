from flask import jsonify, abort
from sqlalchemy.orm import sessionmaker
from database.base import engine
from models.incidentreport_model import IncidentReport
from models.safezone_model import SafeZone
from models.user_model import User
from sqlalchemy.orm import joinedload

Session = sessionmaker(bind=engine)

## DATA

def get_all_users_safe_zones_incidents_service(session):
    try:
        # Fetch all data
        users = session.query(User).options(
            joinedload(User.profile),
            joinedload(User.safe_zones),
            joinedload(User.incident_reports)
        ).all()

        incident_reports = session.query(IncidentReport).all()
        safe_zones = session.query(SafeZone).all()

        # Format the data
        users_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "activity_status": user.profile.activity_status if user.profile else None,
                "profile_picture_url": user.profile.profile_picture_url if user.profile else None,
            }
            for user in users
        ]

        incidents_data = [ir.to_dict() for ir in incident_reports]
        safezones_data = [sz.to_dict() for sz in safe_zones]

        # Final structured response
        result = {
            "users": users_data,
            "incident_reports": incidents_data,
            "safe_zones": safezones_data
        }

        return result

    except Exception as e:
        return {"error": str(e)}

    

## SAFEZONES AND INCIDENTS

def get_users_with_incidents_and_safe_zones_service(session):
    try:
        users = session.query(User).all()
        result = []

        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username, 
                "activity_status": user.profile.activity_status,
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
                "activity_status": user.profile.activity_status,
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
                "activity_status": user.profile.activity_status,
                "email": user.email,  # Assuming `email` is a field in your User model
                "profile_picture_url": user.profile.profile_picture_url if user.profile else None, 
                "safe_zones": [safe_zone.to_dict() for safe_zone in user.safe_zones]
            }
            result.append(user_data)

        return result
    except Exception as e:
        return str(e)


