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
            "longitude": profile_obj.longitude,
            "profile_picture": profile_obj.profile_picture
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

# Upload Profile Picture to Firebase Storage
def upload_profile_picture(user_id, file_path):
    """Uploads a profile picture to Firebase Storage and returns the URL."""
    bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")  # 🔹 Load bucket name from .env
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # 🔹 Define the file path in Firebase Storage (e.g., "profile_pictures/user_id.jpg")
    blob = bucket.blob(f"profile_pictures/{user_id}.jpg")

    # 🔹 Upload the image
    blob.upload_from_filename(file_path)

    # 🔹 Make the image publicly accessible
    blob.make_public()
    download_url = blob.public_url

    print(f"Profile picture uploaded: {download_url}")
    return download_url  # 🔹 Return the image URL

# Save Profile Picture in Database
def update_profile_picture_in_db(user_id, profile_picture_url):
    """Updates the user's profile picture URL in the database."""
    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj:
            return False, "Profile not found"

        # 🔹 Update the profile picture URL in the database
        profile_obj.profile_picture = profile_picture_url
        session.commit()
        return True, "Profile picture updated successfully"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

# Upload Profile Picture API
@profile_controller.route('/upload-profile-picture', methods=['POST'])
@cross_origin()
def upload_profile_picture_api():
    """API to handle profile picture uploads."""
    user_id = request.form.get("user_id")
    file = request.files.get("file")

    if not user_id or not file:
        return jsonify({"error": "Missing user_id or file"}), 400

    # Save file temporarily
    file_path = f"/tmp/{user_id}.jpg"
    file.save(file_path)

    # Upload to Firebase Storage
    profile_picture_url = upload_profile_picture(user_id, file_path)

    # Update the database with the profile picture URL
    success, message = update_profile_picture_in_db(user_id, profile_picture_url)

    if success:
        return jsonify({"message": message, "profile_picture_url": profile_picture_url}), 200
    else:
        return jsonify({"error": message}), 500

# Get Profile Picture API
@profile_controller.route('/get-profile-picture/<int:user_id>', methods=['GET'])
def get_profile_picture(user_id):
    """API to fetch the user's profile picture URL."""
    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj or not profile_obj.profile_picture:
            return jsonify({"error": "Profile picture not found"}), 404
        return jsonify({"profile_picture_url": profile_obj.profile_picture}), 200
    finally:
        session.close()
