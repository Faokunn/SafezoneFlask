from flask import jsonify, abort
from sqlalchemy.orm import sessionmaker
from models.dangerzone_model import DangerZone
from database.base import engine

Session = sessionmaker(bind=engine)

def get_danger_zone_by_id_service(danger_zone_id, session):
    try:
        danger_zone = session.query(DangerZone).filter(DangerZone.id == danger_zone_id).first()
        if not danger_zone:
            abort(404, description="Danger zone not found")

        return jsonify(danger_zone.to_dict()), 200

    except Exception as e:
        abort(500, description=f"Error retrieving danger zone: {str(e)}")

def get_all_danger_zones_service(session):
    try:
        danger_zones = session.query(DangerZone).all()

        danger_zones_data = [danger_zone.to_dict() for danger_zone in danger_zones]

        return jsonify(danger_zones_data), 200

    except Exception as e:
        abort(500, description=f"Error retrieving danger zones: {str(e)}")

def get_all_verified_danger_zones_service(session):
    try:
        danger_zones = session.query(DangerZone).filter_by(is_verified=True).all()

        danger_zones_data = [danger_zone.to_dict() for danger_zone in danger_zones]

        return jsonify(danger_zones_data), 200

    except Exception as e:
        abort(500, description=f"Error retrieving danger zones: {str(e)}")
