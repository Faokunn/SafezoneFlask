import json
from database.base import firebase_admin
from firebase_admin import firestore
from flask import Blueprint, request, jsonify
from database.base import SessionLocal
from models.groupmembers_model import GroupMember
from models.notifications import Notification
from models.profile_model import Profile
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
import os
from database.base import db
from flask_cors import cross_origin
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base



# Load environment variables from .env file
load_dotenv()

notification_controller = Blueprint('notification_controller', __name__)

# Create Notification
@notification_controller.route('/create_notif', methods=['POST'])
@cross_origin()
def create_notification():
    data = request.json
    user_id = data.get("user_id")
    title = data.get("title")
    message = data.get("message")
    type = data.get("type")
    is_done = data.get("is_done", False)  # Default to False if not provided

    if not all([user_id, title, message, type]):
        return jsonify({"error": "Missing required fields"}), 400

    session = SessionLocal()
    try:
        new_notification = Notification(
            user_id=user_id, 
            title=title, 
            message=message, 
            type=type, 
            is_done=is_done  # Add is_done field
        )
        session.add(new_notification)
        session.commit()
        return jsonify({"message": "Notification created successfully!"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Get Notifications for a User
@notification_controller.route('/get_notif/<int:user_id>', methods=['GET'])
@cross_origin()
def get_notifications(user_id):
    session = SessionLocal()
    try:
        notifications = session.query(Notification).filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        return jsonify([{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "is_done": n.is_done,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "type": n.type
        } for n in notifications]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()



# Get Unread Notifications Count
@notification_controller.route('/unread-count/<int:user_id>', methods=['GET'])
@cross_origin()
def get_unread_notifications_count(user_id):
    session = SessionLocal()
    try:
        unread_count = session.query(Notification).filter_by(user_id=user_id, is_read=False).count()
        return jsonify({"unread_count": unread_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# Mark Notification as Read
@notification_controller.route('/mark_notif/<int:notification_id>', methods=['PATCH'])
@cross_origin()
def mark_notification_as_read(notification_id):
    session = SessionLocal()
    try:
        notification = session.query(Notification).filter_by(id=notification_id).first()
        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        notification.is_read = True  # Mark the notification as done
        session.commit()
        return jsonify({"message": "Notification marked as read"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Delete Notification
@notification_controller.route('/delete_notif/<int:notification_id>', methods=['DELETE'])
@cross_origin()
def delete_notification(notification_id):
    session = SessionLocal()
    try:
        notification = session.query(Notification).filter_by(id=notification_id).first()
        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        session.delete(notification)
        session.commit()
        return jsonify({"message": "Notification deleted successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
#broadcast to every Circle Members
@notification_controller.route('/broadcast', methods=['POST'])
@cross_origin()
def send_notification_to_circle_members():
    data = request.json
    user_id = data.get("user_id")
    title = data.get("title")
    message = data.get("message")
    type = data.get("type")
    is_done = data.get("is_done", False)  # Default to False if not provided

    if not all([user_id, title, message, type]):
        return jsonify({"error": "Missing required fields"}), 400

    session = SessionLocal()
    try:
        # Get all circles where the user is a member
        user_circles = session.query(GroupMember.circle_id).filter_by(user_id=user_id).all()
        circle_ids = [circle.circle_id for circle in user_circles]

        if not circle_ids:
            return jsonify({"error": "User is not in any circles"}), 404

        # Get all group members in those circles
        group_members = session.query(GroupMember.user_id).filter(GroupMember.circle_id.in_(circle_ids)).distinct().all()
        member_ids = [member.user_id for member in group_members if member.user_id != user_id]  # Exclude the sender

        if not member_ids:
            return jsonify({"error": "No members found in user's circles"}), 404

        # Create notifications for all members
        notifications = [
            Notification(user_id=member_id, title=title, message=message, type=type, is_done=is_done)
            for member_id in member_ids
        ]
        session.bulk_save_objects(notifications) 
        session.commit()
        # gello

        return jsonify({"message": f"Notification sent to {len(member_ids)} group members"}), 201

    except Exception as e:
        session.rollback()

        
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

#Broadcast to nearest police station
@notification_controller.route('/broadcastpolicestation', methods=['POST'])
@cross_origin()
def send_notification_to_nearest_station():
    data = request.json
    title = data.get("title")
    message = data.get("message")
    type = data.get("type")
    police_station_name = data.get("police_station_name")
    is_done = data.get("is_done", False)  # Default to False if not provided

    if not all([title, message, type, police_station_name]):
        return jsonify({"error": "Missing required fields"}), 400

    session = SessionLocal()
    try:
        # Find the police station user
        police_station_user = (
            session.query(Profile)
            .filter(
                func.trim(func.concat(Profile.first_name, ' ', Profile.last_name)) == police_station_name
            )
            .first()
        )

        if not police_station_user:
            return jsonify({"error": f"Police station '{police_station_name}' not found"}), 404

        # Create the notification for that user
        new_notification = Notification(
            user_id=police_station_user.id, 
            title=title, 
            message=message, 
            type=type, 
            is_done=is_done
        )
        session.add(new_notification)
        session.commit()
        return jsonify({"message": f"Notification sent to {police_station_name}!"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# Get Unread Notifications Count
@notification_controller.route('/unread/<int:user_id>', methods=['GET'])
@cross_origin()
def get_new_unread_notifications(user_id):
    last_checked = request.args.get("last_checked")  # Expected in "YYYY-MM-DDTHH:MM:SS" format
    
    session = SessionLocal()
    try:
        query = session.query(Notification).filter_by(user_id=user_id, is_read=False)

        if last_checked:
            try:
                last_checked_time = datetime.fromisoformat(last_checked)
                query = query.filter(Notification.created_at > last_checked_time)
            except ValueError:
                return jsonify({"error": "Invalid timestamp format"}), 400

        # Sort by newest first
        unread_notifications = query.order_by(Notification.created_at.desc()).all()

        latest_timestamp = max(
            (n.created_at for n in unread_notifications),
            default=datetime.now()
        ).strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "unread_count": len(unread_notifications),
            "notifications": [{
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "type": n.type
            } for n in unread_notifications],
            "last_checked": latest_timestamp
        }), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
#Mark As Done
@notification_controller.route('/mark_done/<int:notification_id>', methods=['PATCH'])
@cross_origin()
def mark_notification_as_done(notification_id):
    session = SessionLocal()
    try:
        notification = session.query(Notification).filter_by(id=notification_id).first()
        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        notification.is_done = True
        session.commit()
        return jsonify({"message": "Notification marked as done"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()