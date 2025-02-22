from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models.user_model import User
from models.profile_model import Profile
from models.contacts_model import ContactModel  # Import the ContactModel
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
    if not profile_obj:
        profile_obj = {}  # Empty dictionary if profile is missing
    return {
        "user": {
            "id": user_obj.id,
            "username": user_obj.username,
            "email": user_obj.email,
        },
        "profile": {
            "address": profile_obj.get("address", "Address not available"),
            "first_name": profile_obj.get("first_name", "").upper(),
            "last_name": profile_obj.get("last_name", "").upper(),
            "is_admin": profile_obj.get("is_admin", False),
            "is_girl": profile_obj.get("is_girl", True),
            "is_verified": profile_obj.get("is_verified", False),
            "status": profile_obj.get("status", "Safe"),
        }
    }


# Emergency contacts for Dagupan City
emergency_contacts = [
    {"name": "Philippine National Police (PNP)", "phone_number": "0916-525-6802"},
    {"name": "Ambulance", "phone_number": "0917-184-2611"},
    {"name": "Firefighter", "phone_number": "0917-184-2611"},
    {"name": "City Disaster Risk Reduction & Management Office (CDRRMO)", "phone_number": "0968-444-9598"},
    {"name": "City Health Office (CHO)", "phone_number": "0933-861-6088"},
    {"name": "Philippine Red Cross Dagupan", "phone_number": "0928-559-2701"},
    {"name": "Public Order & Safety Office (POSO)", "phone_number": "0967-435-7097"},
    {"name": "Anti-Violence Against Women and Children (VAWC) Helpline", "phone_number": "0933-378-8888"},
    {"name": "Anti-Bullying Helpline", "phone_number": "0960-260-6036"},
    {"name": "Anti-Suicide Helpline", "phone_number": "0969-045-1111"},
]

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
    is_verified = data.get('is_verified', False)
    status = data.get('status', "Safe")  # Default to False

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
            is_verified=is_verified,
            status=status,
        )
        session.add(profile)
        session.commit()

        # Add emergency contacts
        for contact in emergency_contacts:
            new_contact = ContactModel(
                user_id=new_user.id,
                name=contact["name"],
                phone_number=contact["phone_number"]
            )
            session.add(new_contact)
        session.commit()

        return jsonify({"message": "User, profile, and emergency contacts created successfully"}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Username or email already exists"}), 400


# Login Route (Return user and profile data)
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')  # Using email instead of username
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user_obj = session.query(User).filter_by(email=email).first()


    if user_obj and user_obj.password == password:  # Compare plain-text passwords
        profile_obj = session.query(Profile).filter_by(user_id=user_obj.id).first()
        
        # Return user and profile data
        return jsonify({
            "user": {
                "id": user_obj.id,
                "username": user_obj.username,
                "email": user_obj.email,
            },
"profile": {
        "address": profile_obj.address if profile_obj.address else "Address not available",
        "first_name": profile_obj.first_name.upper() if profile_obj.first_name else "",
        "last_name": profile_obj.last_name.upper() if profile_obj.last_name else "",
        "is_admin": profile_obj.is_admin if profile_obj.is_admin is not None else False,
        "is_girl": profile_obj.is_girl if profile_obj.is_girl is not None else True,
        "is_verified": profile_obj.is_verified if profile_obj.is_verified is not None else False,
        "status": profile_obj.status if profile_obj.status else "Safe"
        }
        }), 200

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
