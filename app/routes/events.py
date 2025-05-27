from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.models import Event

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
        }
        for reg in event.registrations
    ]

    return jsonify(registrants=registrants), 200
