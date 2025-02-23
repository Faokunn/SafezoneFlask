import json
from app import firebase_admin
from firebase_admin import firestore
from flask import Blueprint, request, jsonify
from database.base import SessionLocal
from models.profile_model import Profile
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import os
from database.base import db
from flask_cors import cross_origin

# Load environment variables from .env file
load_dotenv()

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
            "status": profile_obj.status,
            "latitude": profile_obj.latitude,
            "longitude": profile_obj.longitude
        }
    }

# Get Profile Info by User ID
@profile_controller.route('/get-profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj:
            return jsonify({"error": "Profile not found"}), 404
        return jsonify(format_profile_data(profile_obj)), 200
    finally:
        session.close()

# Update User Location
@profile_controller.route('/update-location', methods=['POST'])
@cross_origin()
def update_location():
    data = request.json
    user_id = data.get("user_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if user_id is None or latitude is None or longitude is None:
        return jsonify({"error": "Missing required fields"}), 400

    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj:
            return jsonify({"error": "Profile not found"}), 404

        # Update the database
        profile_obj.latitude = latitude
        profile_obj.longitude = longitude
        session.commit()

        # Update Firebase Firestore for real-time tracking
        db.collection("locations").document(str(user_id)).set({ 
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        return jsonify({"message": "Location updated!"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# Update User Status
@profile_controller.route('/update-status', methods=['PATCH'])
@cross_origin()
def update_status():
    data = request.json
    user_id = data.get("user_id")
    status = data.get("status")

    if user_id is None or status is None:
        return jsonify({"error": "Missing required fields"}), 400

    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj:
            return jsonify({"error": "Profile not found"}), 404

        # Update the status field
        profile_obj.status = status
        session.commit()

        return jsonify({"message": "Status updated!", "status": status}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()