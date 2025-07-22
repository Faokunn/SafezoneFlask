from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from models.circle_model import Circle
from models.profile_model import Profile
from models.user_model import User
from models.groupmembers_model import GroupMember
from database.base import engine
import random
import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Blueprint for circle routes
circle_controller = Blueprint('circle_controller', __name__)

def generate_unique_code():
    while True:
        code = str(random.randint(10000, 99999))
        existing_circle = session.query(Circle).filter_by(code=code).first()
        if not existing_circle:
            return code

# Generate a temporary join code
@circle_controller.route('/generate_code', methods=['POST'])
def generate_code():
    data = request.get_json()
    circle_id = data.get('circle_id')
    
    if not circle_id:
        return jsonify({"error": "Circle ID is required"}), 400

    circle = session.query(Circle).filter_by(id=circle_id).first()
    
    if not circle:
        return jsonify({"error": "Circle not found"}), 404
    
    # Generate a unique code and set an expiration time
    circle.code = generate_unique_code()
    circle.code_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    session.commit()

    return jsonify({"message": "Code generated successfully", "code": circle.code, "expires_at": circle.code_expiry}), 200

# Create a circle
@circle_controller.route('/create_circle', methods=['POST'])
def create_circle():
    data = request.get_json()

    name = data.get('name')
    user_id = data.get('user_id')  # The user who is creating the circle
    
    if not name or not user_id:
        return jsonify({"error": "Circle name and user ID are required"}), 400

    try:
        # Create the new circle with a null code
        new_circle = Circle(name=name, code=None, code_expiry=None)
        session.add(new_circle)
        session.commit()

        # Add the user who created the circle as the first member
        group_member = GroupMember(user_id=user_id, circle_id=new_circle.id)
        session.add(group_member)
        session.commit()

        try:
            from firebase_admin import firestore
            db = firestore.client()

            user_ref = db.collection("locations").document(str(user_id))

            current_data = user_ref.get()
            existing_sharing = current_data.to_dict().get("circleSharing", {}) if current_data.exists else {}

            existing_sharing[str(new_circle.id)] = True

            user_ref.set({
                "circleSharing": existing_sharing
            }, merge=True)

        except Exception as e:
            return jsonify({"error": f"Failed to update Firestore after join: {str(e)}"}), 500

        return jsonify({"message": "Circle created successfully", "circle_id": new_circle.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

# Join a circle using the code
@circle_controller.route('/join_circle', methods=['POST'])
def join_circle():
    data = request.get_json()
    user_id = data.get('user_id')
    code = data.get('code')

    if not user_id or not code:
        return jsonify({"error": "User ID and circle code are required"}), 400

    try:
        # Ensure code is a string before querying
        circle = session.query(Circle).filter(Circle.code == str(code)).first()
        
        if not circle:
            return jsonify({"error": "Invalid circle code"}), 404

        # Check if user already in circle
        existing_member = session.query(GroupMember).filter_by(user_id=user_id, circle_id=circle.id).first()
        if existing_member:
            return jsonify({"message": "User already in this circle"}), 200

        # Add user to the circle
        new_member = GroupMember(user_id=user_id, circle_id=circle.id)
        session.add(new_member)
        session.commit()

        try:
            from firebase_admin import firestore
            db = firestore.client()

            user_ref = db.collection("location").document(str(user_id))

            current_data = user_ref.get()
            existing_sharing = current_data.get("circleSharing", {}) if current_data.exists else {}

            existing_sharing[str(circle.id)] = True

            user_ref.set({
                "circleSharing": existing_sharing},
                merge=True)
        except Exception as e:
            return jsonify({"error": f"Failed to update Firestore after join: {str(e)}"}), 500

        return jsonify({"message": "User successfully joined the circle"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
# Remove a user from a circle
@circle_controller.route('/remove_member', methods=['POST'])
def remove_member():
    data = request.get_json()

    user_id = data.get('user_id')
    circle_id = data.get('circle_id')

    if not user_id or not circle_id:
        return jsonify({"error": "User ID and Circle ID are required"}), 400

    group_member = session.query(GroupMember).filter_by(user_id=user_id, circle_id=circle_id).first()

    if not group_member:
        return jsonify({"error": "User is not a member of this circle"}), 404

    session.delete(group_member)
    session.commit()

    return jsonify({"message": "User removed from the circle successfully"}), 200

# View all users in a circle
@circle_controller.route('/view_members', methods=['GET'])
def view_members():
    circle_id = request.args.get('circle_id')

    if not circle_id:
        return jsonify({"error": "Circle ID is required"}), 400

    circle = session.query(Circle).filter_by(id=circle_id).first()

    if not circle:
        return jsonify({"error": "Circle not found"}), 404

    # Get all users who are members of the circle
    members = session.query(User).join(GroupMember).filter(GroupMember.circle_id == circle_id).all()

    if not members:
        return jsonify({"message": "No members in this circle"}), 200

    # Fetch profile data for each member
    members_data = []
    for member in members:
        profile = session.query(Profile).filter_by(user_id=member.id).first()
        members_data.append({
            "user_id": member.id,
            "first_name": profile.first_name if profile else "",
            "last_name": profile.last_name if profile else "",
            "profile_picture": profile.profile_picture_url if profile else "",
            "status": profile.status if profile else "Safe",
            "latitude": profile.latitude if profile else 0.0,
            "longitude": profile.longitude if profile else 0.0,
        })

    return jsonify({"circle_id": circle_id, "members": members_data}), 200


# View all circles of a user
@circle_controller.route('/view_user_circles', methods=['GET'])
def view_user_circles():
    user_id = request.args.get('user_id')  # Get user_id

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Get all circles where the user is a member
    circles = (
        session.query(Circle)
        .join(GroupMember, Circle.id == GroupMember.circle_id)
        .filter(GroupMember.user_id == user_id)
        .all()
    )

    if not circles:
        return jsonify({"message": "No circles found for this user"}), 200

    circles_data = []
    for circle in circles:
        # Get is_active status from GroupMember table
        group_member = session.query(GroupMember).filter_by(user_id=user_id, circle_id=circle.id).first()
        is_active = group_member.is_active if group_member else False

        circles_data.append({
            "circle_id": circle.id,
            "circle_name": circle.name,
            "code": circle.code,
            "status": is_active
        })

    return jsonify({"user_id": user_id, "circles": circles_data}), 200

# Change circle is_active status
@circle_controller.route('/update_active_status', methods=['PATCH'])
def update_active_status():
    data = request.get_json()
    user_id = data.get('user_id')  # User whose active circle is being changed
    circle_id = data.get('circle_id')  # The circle to activate
    is_active = data.get('is_active')  # True or False

    if not user_id or not circle_id or is_active is None:
        return jsonify({"error": "User ID, Circle ID, and is_active status are required"}), 400

    group_member = session.query(GroupMember).filter_by(user_id=user_id, circle_id=circle_id).first()

    if not group_member:
        return jsonify({"error": "User is not a member of this circle"}), 404

    try:
        if is_active:
            # Deactivate all other circles for this user
            session.query(GroupMember).filter(
                GroupMember.user_id == user_id,  # Only for this user
                GroupMember.circle_id != circle_id,  # Exclude the target circle
                GroupMember.is_active == True  # Only update currently active circles
            ).update({"is_active": False}, synchronize_session=False)

            # Commit the change before updating the target circle
            session.commit()

        # Set the target circle's active status
        group_member.is_active = bool(is_active)
        session.commit()

        return jsonify({
            "message": "User's active circle updated successfully",
            "user_id": user_id,
            "active_circle_id": circle_id if is_active else None,
            "is_active": group_member.is_active
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500


