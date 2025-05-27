from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import Event, User
from app import db
from app.utils.decorators import (
    admin_required,
    super_admin_required,
)

bp = Blueprint("admin", __name__)


@bp.route("/admin/new", methods=["POST"])
@jwt_required()
@admin_required
def create_event():
    data = request.get_json()
    required_fields = [
        "title",
        "description",
        "date",
        "channel",
        "language",
        "location",
        "group_size",
        "num_instructors_needed",
        "num_representatives_needed",
    ]

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        event_date = datetime.fromisoformat(data["date"])
    except (ValueError, KeyError):
        return jsonify({"message": "Invalid date format. Use ISO 8601."}), 400

    event = Event(
        title=data["title"],
        description=data["description"],
        date=event_date,
        channel=data["channel"],
        language=data["language"],
        location=data["location"],
        group_size=data.get("group_size", 0),
        num_instructors_needed=data.get("num_instructors_needed", 0),
        num_representatives_needed=data.get("num_representatives_needed", 0),
        status="pending",
    )
    db.session.add(event)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "Event created",
                "event": {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "date": event.date.isoformat(),
                    "channel": event.channel,
                    "language": event.language,
                    "location": event.location,
                    "status": event.status,
                    "group_size": event.group_size,
                    "num_instructors_needed": event.num_instructors_needed,
                    "num_representatives_needed": event.num_representatives_needed,
                },
            }
        ),
        201,
    )


@bp.route("/admin/edit/<int:event_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    data = request.get_json()

    if "title" in data:
        event.title = data["title"]
    if "description" in data:
        event.description = data["description"]
    if "date" in data:
        try:
            event.date = datetime.fromisoformat(data["date"])
        except ValueError:
            return jsonify({"message": "Invalid date format"}), 400
    if "channel" in data:
        event.channel = data["channel"]
    if "language" in data:
        event.language = data["language"]
    if "location" in data:
        event.location = data["location"]
    if "status" in data:
        event.status = data["status"]
    if "group_size" in data:
        event.group_size = data["group_size"]
    if "num_instructors_needed" in data:
        event.num_instructors_needed = data["num_instructors_needed"]
    if "num_representatives_needed" in data:
        event.num_representatives_needed = data["num_representatives_needed"]

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

    return jsonify({"message": "Event updated"}), 200


@bp.route("/admin/delete/<int:event_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    try:
        db.session.delete(event)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "Failed to delete event", "error": str(e)}),
            500,
        )

    return jsonify({"message": "Event and all registrations deleted successfully"}), 200


@bp.route("/admin/approve/<int:event_id>", methods=["PUT"])
@jwt_required()
@admin_required
def approve_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    event.status = "approved"

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

    return jsonify({"message": "Event approved"}), 200


@bp.route("/admin/unapprove/<int:event_id>", methods=["PUT"])
@jwt_required()
@admin_required
def set_event_pending(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    event.status = "pending"

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

    return jsonify({"message": "Event status set to pending"}), 200


@bp.route("/admin/set-permission/<int:user_id_to_change>", methods=["PUT"])
@jwt_required()
@super_admin_required
def set_user_permission(user_id_to_change):
    data = request.get_json()
    new_permission = data.get("permission_type")

    if not new_permission or new_permission not in ["user", "admin", "super_admin"]:
        return (
            jsonify(
                {
                    "message": "Invalid permission type. Must be 'user', 'admin', or 'super_admin'."
                }
            ),
            400,
        )

    target_user = User.query.get(user_id_to_change)
    if not target_user:
        return jsonify({"message": "Target user not found."}), 404

    target_user.permission_type = new_permission
    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"User '{target_user.email}' permission updated to '{new_permission}'."
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"message": "Failed to update user permission.", "error": str(e)}),
            500,
        )
