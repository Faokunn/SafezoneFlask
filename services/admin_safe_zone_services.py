from flask import jsonify, abort
from sqlalchemy.orm import sessionmaker
from database.base import engine
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.exc import IntegrityError
from models.safezone_model import SafeZone
from models.safe_zone_status_history import SafeZoneStatusHistory

Session = sessionmaker(bind=engine)

def add_status_history(session, safe_zone_id, status, remarks=None):
    status_history = SafeZoneStatusHistory(
        safe_zone_id=safe_zone_id,
        status=status,
        timestamp=datetime.now(),
        remarks=remarks,
    )
    session.add(status_history)

def update_safe_zone_status(safe_zone_id, session, status, remarks, is_verified=None):
    safe_zone = session.query(SafeZone).filter_by(id=safe_zone_id).first()
    if not safe_zone:
        abort(404, description="Safe zone not found")

    safe_zone.status = status
    if is_verified is not None:
        safe_zone.is_verified = is_verified

    session.add(safe_zone)
    add_status_history(session, safe_zone_id, status, remarks)
    session.commit()

    return jsonify({
        "message": f"Safe zone {safe_zone_id} {status}.",
        "safe_zone": {
            "id": safe_zone.id,
            "status": safe_zone.status,
            "is_verified": safe_zone.is_verified,
        }
    }), 200

def verify_safe_zone_service(safe_zone_id, session):
    return update_safe_zone_status(
        safe_zone_id, session, "verified", "Safe zone report verified.", is_verified=True
    )

def reject_safe_zone_service(safe_zone_id, session):
    return update_safe_zone_status(
        safe_zone_id, session, "rejected", "Safe zone rejected.", is_verified=False
    )

def under_review_safe_zone_service(safe_zone_id, session):
    return update_safe_zone_status(
        safe_zone_id, session, "under review", "Safe zone is under review."
    )
