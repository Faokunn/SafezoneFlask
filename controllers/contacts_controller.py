from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from models.contacts_model import ContactModel
from models.user_model import User
from database.base import engine
from sqlalchemy.exc import IntegrityError

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Blueprint for contact routes
contact_controller = Blueprint('contact_controller', __name__)

# Create a new contact for a user
@contact_controller.route('/create_contact/<int:user_id>', methods=['POST'])
def create_contact(user_id):
    data = request.get_json()

    name = data.get('name')
    phone_number = data.get('phone_number')

    if not name or not phone_number:
        return jsonify({"error": "Missing name or phone number"}), 400

    # Check if the user exists
    user_obj = session.query(User).filter_by(id=user_id).first()
    if not user_obj:
        return jsonify({"error": "User not found"}), 404

    try:
        # Create a new contact
        new_contact = ContactModel(user_id=user_id, name=name, phone_number=phone_number)
        session.add(new_contact)
        session.commit()

        return jsonify({"message": "Contact created successfully"}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Error creating contact"}), 400

# Get all contacts by user ID
@contact_controller.route('/get_contacts/<int:user_id>', methods=['GET'])
def get_contacts(user_id):
    # Check if the user exists
    user_obj = session.query(User).filter_by(id=user_id).first()
    if not user_obj:
        return jsonify({"error": "User not found"}), 404

    # Fetch all contacts for the user
    contacts = session.query(ContactModel).filter_by(user_id=user_id).all()
    contact_list = []

    for contact in contacts:
        contact_list.append({
            "id": contact.id,
            "name": contact.name,
            "phone_number": contact.phone_number
        })
    
    return jsonify(contact_list), 200

# Delete a contact by contact ID
@contact_controller.route('/delete_contact/<int:user_id>/<int:contact_id>', methods=['DELETE'])
def delete_contact(user_id, contact_id):
    # Check if the user exists
    user_obj = session.query(User).filter_by(id=user_id).first()
    if not user_obj:
        return jsonify({"error": "User not found"}), 404

    # Fetch the contact to delete
    contact = session.query(ContactModel).filter_by(user_id=user_id, id=contact_id).first()

    if not contact:
        return jsonify({"error": "Contact not found"}), 404

    try:
        # Delete the contact
        session.delete(contact)
        session.commit()

        return jsonify({"message": "Contact deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
