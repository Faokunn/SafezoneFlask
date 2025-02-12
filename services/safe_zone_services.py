from flask import jsonify, abort
from sqlalchemy.orm import sessionmaker
from models.safe_zone_status_history import SafeZoneStatusHistory
from models.safezone_model import SafeZone
from database.base import engine
from models.user_model import User
from datetime import datetime
from zoneinfo import ZoneInfo


Session = sessionmaker(bind=engine)

def add_status_history(session, safe_zone_id, status, remarks=None):
    status_history = SafeZoneStatusHistory(
        safe_zone_id=safe_zone_id,
        status=status,
        timestamp=datetime.now(),
        remarks=remarks,
    )
    session.add(status_history)

def parse_report_timestamp(timestamp):
    try:
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Manila"))
        return timestamp.astimezone(ZoneInfo("Asia/Manila"))
    except Exception as e:
        abort(400, description=f"Invalid report_timestamp: {str(e)}")

## GET

def get_safe_zone_by_id_service(safe_zone_id, session):
    try:
        safe_zone = session.query(SafeZone).filter(SafeZone.id == safe_zone_id).first()
        if not safe_zone:
            abort(404, description="Safe zone not found")

        return jsonify(safe_zone.to_dict()), 200

    except Exception as e:
        abort(500, description=f"Error retrieving safe zone: {str(e)}")

def get_all_safe_zones_service(session):
    try:
        safe_zones = session.query(SafeZone).all()

        safe_zones_data = [safe_zone.to_dict() for safe_zone in safe_zones]

        return jsonify(safe_zones_data), 200

    except Exception as e:
        abort(500, description=f"Error retrieving safe zones: {str(e)}")

def get_all_verified_safe_zones_service(session):
    try:
        safe_zones = session.query(SafeZone).filter_by(is_verified=True).all()

        safe_zones_data = [safe_zone.to_dict() for safe_zone in safe_zones]

        return jsonify(safe_zones_data), 200

    except Exception as e:
        abort(500, description=f"Error retrieving verified safe zones: {str(e)}")

def get_safe_zones_by_status_service(status, session):
    try:
        safe_zones = session.query(SafeZone).filter_by(status=status).all()
        return safe_zones
    except Exception as e:
        return str(e)
    
def get_safe_zones_by_user_id_service(user_id, session):
    try:
        safe_zones = session.query(SafeZone).filter_by(user_id=user_id).all()
        return safe_zones
    except Exception as e:
        return str(e)

def get_status_history_service(session, safe_zone_id):
    try:
        status_history = (
            session.query(SafeZoneStatusHistory)
            .filter(SafeZoneStatusHistory.safe_zone_id == safe_zone_id)
            .order_by(SafeZoneStatusHistory.timestamp.desc())  
            .all()
        )
        
        return [status.to_dict() for status in status_history]
    
    except Exception as e:
        return {"error": str(e)}

## CREATE

def create_safe_zone_service(data, session):
    try:

        user = session.query(User).filter_by(id=data['user_id']).first()
        if not user:
            abort(404, description="User not found") 

        report_timestamp = parse_report_timestamp(data['report_timestamp'])
        
        safe_zone = SafeZone(
            user_id=data['user_id'],
            is_verified=data.get("is_verified", False),
            latitude=data["latitude"],
            longitude=data["longitude"],
            radius=data["radius"],
            name=data["name"],
            scale=data["scale"],
            description=data["description"],
            time_of_day=data["time_of_day"],
            frequency=data["frequency"],
            status="pending",
            report_timestamp=report_timestamp,
        )
        session.add(safe_zone)
        session.flush()  

        add_status_history(session, safe_zone_id=safe_zone.id, status="pending", remarks="Safe zone pending.")

        session.commit()
        session.refresh(safe_zone) 
        return safe_zone.to_dict()
    except Exception as e:
        session.rollback()
        raise e

def update_safe_zone_service(safe_zone_id, data, session):
    try:
        safe_zone = session.query(SafeZone).filter(SafeZone.id == safe_zone_id).first()
        if not safe_zone:
            return None

        safe_zone.is_verified = data.get("is_verified", safe_zone.is_verified)
        safe_zone.latitude = data.get("latitude", safe_zone.latitude)
        safe_zone.longitude = data.get("longitude", safe_zone.longitude)
        safe_zone.radius = data.get("radius", safe_zone.radius)
        safe_zone.name = data.get("name", safe_zone.name)
        safe_zone.scale = data.get("scale", safe_zone.scale)
        safe_zone.description = data.get("description", safe_zone.description)
        safe_zone.time_of_day = data.get("time_of_day", safe_zone.time_of_day)
        safe_zone.frequency = data.get("frequency", safe_zone.frequency)

        session.commit()
        return safe_zone.to_dict()
    except Exception as e:
        session.rollback()
        raise e

## DELETE

def delete_safe_zone_service(safe_zone_id, session):
    try:
        safe_zone = session.query(SafeZone).filter_by(id=safe_zone_id).first()
        if not safe_zone:
            return {"message": "Safe Zone not found"}
        session.delete(safe_zone)
        session.commit()
        return {"message": f"Safe Zone {safe_zone_id} deleted successfully"}
    except Exception as e:
        session.rollback()
        return str(e)

