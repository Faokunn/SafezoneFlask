from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models.user_model import User
from models.profile_model import Profile
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from database.base import engine
from flask_jwt_extended import create_access_token

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Blueprint for user routes
user_controller = Blueprint('user_controller', __name__)

def format_user_data(user_obj, profile_obj):
    return {
        "user": {
            "id": user_obj.id,
            "username": user_obj.username,
            "email": user_obj.email,
        },
        "profile": {
            "address": profile_obj.address,
            "first_name": profile_obj.first_name.upper(),
            "last_name": profile_obj.last_name.upper(),
            "is_admin": profile_obj.is_admin,
            "is_girl": profile_obj.is_girl,
            "is_verified": profile_obj.is_verified,
        }
    }

# Create Account Route
@user_controller.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')  # No hashing now
    address = data.get('address')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    
    # Get optional profile values with defaults if not provided
    is_admin = data.get('is_admin', False)  # Default to False
    is_girl = data.get('is_girl', True)     # Default to True
    is_verified = data.get('is_verified', False)  # Default to False

    if not username or not email or not password or not address or not first_name or not last_name:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Create user (no password hashing)
        new_user = User(username=username, email=email, password=password)  # Store password as plain text
        session.add(new_user)
        session.commit()

        # Create user profile with optional fields
        profile = Profile(
            first_name=first_name,
            last_name=last_name,
            address=address,
            user_id=new_user.id,  # Link the profile to the user
            is_admin=is_admin,
            is_girl=is_girl,
            is_verified=is_verified
        )
        session.add(profile)
        session.commit()

        return jsonify({"message": "User and profile created successfully"}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Username or email already exists"}), 400



# Login Route
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')  # Using email instead of username
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user_obj = session.query(User).filter_by(email=email).first() 

    if user_obj and user_obj.password == password: 
        # Create JWT token
        access_token = create_access_token(identity=user_obj.id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid credentials"}), 401


# Get All Users Route - NO TOKEN REQUIRED
@user_controller.route('/users', methods=['GET'])
def get_all_users():
    users = session.query(User).all()
    user_list = []
    
    for user_obj in users:
        profile_obj = session.query(Profile).filter_by(user_id=user_obj.id).first()
        user_data = format_user_data(user_obj, profile_obj)
        user_list.append(user_data)
    
    return jsonify(user_list), 200
