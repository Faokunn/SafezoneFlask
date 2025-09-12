
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
from sqlalchemy import func

load_dotenv()

admin_users_controller = Blueprint('admin_users_controller', __name__)

@admin_users_controller.route('/approve-admin/<int:user_id>', methods=['PATCH'])
@cross_origin()
def approve_admin(user_id):
    session = SessionLocal()
    try:
        profile_obj = session.query(Profile).filter_by(user_id=user_id).first()
        if not profile_obj:
            return jsonify({"error": "Profile not found"}), 404

        profile_obj.is_admin = True
        profile_obj.is_verified = True # to do: add a new field (admin_request_pending) instead of using is_verified), temp muna ito
        session.commit()

        return jsonify({"message": f"User {user_id} is now an admin!"}), 200
    finally:
        session.close()


@admin_users_controller.route('/admin-requests', methods=['GET'])
@cross_origin()
def get_admin_requests():
    session = SessionLocal()
    try:
        requests = session.query(Profile).filter_by(is_verified=False).all()
        return jsonify([p.to_dict() for p in requests]), 200
    finally:
        session.close()
