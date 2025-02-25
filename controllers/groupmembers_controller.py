from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from models.groupmembers_model import GroupMember
from models.profile_model import Profile
from database.base import engine
import random
import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Blueprint for circle routes
groupmember_controller = Blueprint('groupmember_controller', __name__)

@groupmember_controller.route('/view_group_members', methods=['GET'])
def view_group_members():
    user_id = request.args.get('user_id')
    circle_id = request.args.get('circle_id')

    if not user_id or not circle_id:
        return jsonify({"error": "User ID and Circle ID are required"}), 400

    # Check if the user is a member of the circle
    is_member = session.query(GroupMember).filter_by(user_id=user_id, circle_id=circle_id).first()
    
    if not is_member:
        return jsonify({"error": "User is not a member of this circle"}), 403

    # Get all users who are members of the circle using an explicit join condition
    members = (
        session.query(Profile)
        .select_from(GroupMember)
        .join(Profile, Profile.id == GroupMember.user_id)  # Explicit join condition
        .filter(GroupMember.circle_id == circle_id)
        .all()
    )

    if not members:
        return jsonify({"message": "No members in this circle"}), 200

    # Fetch profile data for each member
    members_data = []
    for member in members:
        members_data.append({
            "user_id": member.user_id,
            "first_name": member.first_name if member.first_name else "",
            "last_name": member.last_name if member.last_name else "",
            "status": member.status if member.status else "Safe",
            "latitude": member.latitude if member.latitude else 0.0,
            "longitude": member.longitude if member.longitude else 0.0,
        })

    return jsonify({"circle_id": circle_id, "members": members_data}), 200
