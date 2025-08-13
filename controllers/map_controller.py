# map_controller.py
from flask import Blueprint, jsonify
from sqlalchemy.orm import sessionmaker
from database.base import engine
from models.dangerzone_model import DangerZone
from models.safezone_model import SafeZone
from services.safe_zone_services import get_all_verified_safe_zones_service
from services.danger_zone_services import get_all_verified_danger_zones_service

Session = sessionmaker(bind=engine)
session = Session()

map_controller = Blueprint('map_controller', __name__)

@map_controller.route("/map-zones", methods=["GET"])
def get_all_map_zones():
    session = Session()  
    try:
        safe_zones = session.query(SafeZone).filter(
            SafeZone.is_verified == True
        ).all()
        
        danger_zones = session.query(DangerZone).filter(
            DangerZone.show_map == True  
        ).all()
        
        safe_zones_data = [sz.to_dict() for sz in safe_zones]
        danger_zones_data = [dz.to_dict() for dz in danger_zones]
        
        print(f"Found {len(safe_zones_data)} safe zones")  
        print(f"Found {len(danger_zones_data)} danger zones")
        
        return jsonify({
            "success": True,
            "safe_zones": safe_zones_data,
            "danger_zones": danger_zones_data,
            "meta": {
                "safe_count": len(safe_zones_data),
                "danger_count": len(danger_zones_data)
            }
        })
        
    except Exception as e:
        session.rollback()
        print(f"Error in /map-zones: {str(e)}")  
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        session.close()
    
