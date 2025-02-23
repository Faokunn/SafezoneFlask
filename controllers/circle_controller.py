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
        return jsonify({"error": "User ID and Code are required"}), 400

    circle = session.query(Circle).filter_by(code=code).first()
    
    if not circle or (circle.code_expiry and circle.code_expiry < datetime.datetime.utcnow()):
        return jsonify({"error": "Invalid or expired code"}), 400

    existing_member = session.query(GroupMember).filter_by(user_id=user_id, circle_id=circle.id).first()
    if existing_member:
        return jsonify({"message": "User is already a member of this circle"}), 400

    group_member = GroupMember(user_id=user_id, circle_id=circle.id)
    session.add(group_member)
    session.commit()

    return jsonify({"message": "User joined the circle successfully"}), 200

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
            "status": profile.status if profile else "Safe",
            "latitude": profile.latitude if profile else 0.0,
            "longitude": profile.longitude if profile else 0.0,
        })

    return jsonify({"circle_id": circle_id, "members": members_data}), 200


# View all circles of a user
@circle_controller.route('/view_user_circles', methods=['GET'])
def view_user_circles():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = session.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get all circles the user is a member of
    circles = session.query(Circle).join(GroupMember).filter(GroupMember.user_id == user_id).all()

    if not circles:
        return jsonify({"message": "User is not a member of any circle"}), 200

    circles_data = [{"circle_id": circle.id, "circle_name": circle.name, "code": circle.code, "time": circle.code_expiry, "status": circle.is_active} for circle in circles]

    return jsonify({"user_id": user_id, "circles": circles_data}), 200

# Change circle is_active status
@circle_controller.route('/update_active_status', methods=['PATCH'])
def update_active_status():
    data = request.get_json()
    circle_id = data.get('circle_id')
    is_active = data.get('is_active')

    if circle_id is None or is_active is None:
        return jsonify({"error": "Circle ID and is_active status are required"}), 400

    circle = session.query(Circle).filter_by(id=circle_id).first()

    if not circle:
        return jsonify({"error": "Circle not found"}), 404

    try:
        if is_active:  
            # Find all users in the target circle
            user_ids = session.query(GroupMember.user_id).filter_by(circle_id=circle_id).all()
            user_ids = [user_id[0] for user_id in user_ids]

            if user_ids:
                # Deactivate all other active circles for these users
                session.query(Circle).filter(
                    Circle.id != circle_id,  # Exclude the current one
                    Circle.is_active == True,
                    Circle.id.in_(
                        session.query(GroupMember.circle_id)
                        .filter(GroupMember.user_id.in_(user_ids))
                    )
                ).update({"is_active": False}, synchronize_session=False)

        # Update the target circle
        circle.is_active = bool(is_active)
        session.commit()

        return jsonify({
            "message": "Circle status updated successfully",
            "circle_id": circle.id,
            "is_active": circle.is_active
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500


