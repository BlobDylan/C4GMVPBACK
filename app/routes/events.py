from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import Event, User, Registration
from app.utils.decorators import admin_required


bp = Blueprint("events", __name__)


@bp.route("/events", methods=["GET"])
def get_events():
    events = Event.query.all()
    events_list = [
        {
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
            "target_audience": event.target_audience,
            "group_description": event.group_description,
            "additional_notes": event.additional_notes,
        }
        for event in events
    ]
    return jsonify({"events": events_list}), 200


@bp.route("/events/<int:event_id>/registrants", methods=["GET"])
def get_registrants(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    registrants = [
        {
            "id": reg.user.id,
            "firstName": reg.user.first_name,
            "lastName": reg.user.last_name,
            "email": reg.user.email,
            "phoneNumber": reg.user.phone_number,
            "role": reg.user.role,
        }
        for reg in event.registrations
    ]

    return jsonify(registrants=registrants), 200


@bp.route("/events/<int:event_id>/registrations/pending", methods=["GET"])
@jwt_required()
@admin_required
def get_event_pending_registrations(event_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.permission_type not in ['admin', 'super_admin']:
        return jsonify({"message": "Admin access required"}), 403

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    registrations = Registration.query.filter_by(event_id=event_id, status='pending').all()
    pending_registrations = [
        {
            "user_id": reg.user_id,
            "user_email": reg.user.email,
            "user_role": reg.user.role,
            "event_id": reg.event_id,
            "event_title": reg.event.title,
            "event_date": reg.event.date.isoformat(),
            "event_channel": reg.event.channel,
            "event_language": reg.event.language,
            "event_location": reg.event.location,
            "status": reg.status,
        }
        for reg in registrations
    ]

    return jsonify(registrations=pending_registrations), 200
