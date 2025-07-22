import json
import os
from database.base import firebase_admin
from firebase_admin import firestore
from flask import Blueprint, request, jsonify
from database.base import SessionLocal
from models.profile_model import Profile
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from database.base import db
from flask_cors import cross_origin
from google.cloud import storage
from firebase_admin import storage

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
            "activity_status": profile_obj.activity_status,
            "status": profile_obj.status,
            "latitude": profile_obj.latitude,
            "longitude": profile_obj.longitude,
            "profile_picture_url": profile_obj.profile_picture_url,
            "age" : profile_obj.age
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
        db.collection("locations").document(str(user_id)).update({ 
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "circleSharing" : {}
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

# Update Aciticy Status
@profile_controller.route('/update-activity-status', methods=['PATCH'])
@cross_origin()
def update_activity_status():
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

# Save Profile Picture in Database
def update_profile_picture_in_db(user_id, profile_picture_url):
    """Updates the user's profile picture URL in the database."""
    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj:
            return False, "Profile not found"

        # 🔹 Update the profile picture URL in the database
        profile_obj.profile_picture_url = profile_picture_url
        session.commit()
        return True, "Profile picture updated successfully"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def upload_profile_picture(user_id, file):
    """Uploads a profile picture to Firebase Storage and returns the URL."""
    bucket = storage.bucket()
    
    blob = bucket.blob(f"profile_pictures/{file}.jpg")
    blob.upload_from_file(file, content_type=file.mimetype)  # ✅ use file-like object
    blob.make_public()

    return blob.public_url        

# Upload Profile Picture API
@profile_controller.route('/upload-profile-picture', methods=['POST'])
@cross_origin()
def upload_profile_picture_api():
    user_id = request.form.get("user_id")
    file = request.files.get("file")  

    if not user_id or not file:
        return jsonify({"error": "Missing user_id or file"}), 400

    try:

        profile_picture_url = upload_profile_picture(user_id, file)
        success, message = update_profile_picture_in_db(user_id, profile_picture_url)

        if success:
            return jsonify({"message": message, "profile_picture_url": profile_picture_url}), 200
        else:
            return jsonify({"error": message}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get Profile Picture API
@profile_controller.route('/get-profile-picture/<int:user_id>', methods=['GET'])
def get_profile_picture(user_id):
    """API to fetch the user's profile picture URL."""
    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj or not profile_obj.profile_picture_url:
            return jsonify({"error": "Profile picture not found"}), 404
        return jsonify({"profile_picture_url": profile_obj.profile_picture_url}), 200
    finally:
        session.close()
