from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.models import Event
from app import db

bp = Blueprint("admin", __name__)


@bp.route("/admin/new", methods=["POST"])
@jwt_required()
def create_event():
    data = request.get_json()
    required_fields = ["title", "description", "date", "location", "spotsAvailable"]

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
        location=data["location"],
        status="pending",
        spotsAvailable=data["spotsAvailable"],
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
                    "date": event.date.isoformat(),
                    "location": event.location,
                },
            }
        ),
        201,
    )


@bp.route("/admin/edit/<int:event_id>", methods=["PUT"])
@jwt_required()
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
    if "location" in data:
        event.location = data["location"]
    if "status" in data:
        event.status = data["status"]
    if "spotsAvailable" in data:
        event.spotsAvailable = data["spotsAvailable"]

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

    return jsonify({"message": "Event updated"}), 200


@bp.route("/admin/delete/<int:event_id>", methods=["DELETE"])
@jwt_required()
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
            jsonify({"message": "Failed to delete event"}),
            500,
        )

    return jsonify({"message": "Event and all registrations deleted successfully"}), 200


@bp.route("/admin/approve/<int:event_id>", methods=["PUT"])
@jwt_required()
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
def unapprove_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    event.status = "pending"

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

    return jsonify({"message": "Event unapproved"}), 200
