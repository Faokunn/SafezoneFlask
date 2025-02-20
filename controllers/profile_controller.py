from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database.base import engine
from models.profile_model import Profile

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

profile_controller = Blueprint('profile_controller', __name__)

def format_profile_data(profile_obj):
    return {
        "profile": {
            "id": profile_obj.id,
            "first_name": profile_obj.first_name.upper(),
            "last_name": profile_obj.last_name.upper(),
            "address": profile_obj.address,
            "is_admin": profile_obj.is_admin,
            "is_girl": profile_obj.is_girl,
            "is_verified": profile_obj.is_verified,
            "status": profile_obj.status
        }
    }

# Get Profile Info by User ID
@profile_controller.route('/get-profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    profile_obj = session.query(Profile).filter_by(user_id=user_id).first()

    if not profile_obj:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify(format_profile_data(profile_obj)), 200