from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Event, Registration
from app import db

bp = Blueprint("user", __name__)


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"message": "User not found"}), 404

    return (
        jsonify(
            {
                "id": user.id,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "phoneNumber": user.phone_number,
                "permissions": user.permission_type,
                "role": user.role,
            }
        ),
        200,
    )


@bp.route("/events/<int:event_id>/register", methods=["POST"])
@jwt_required()
def register_for_event(event_id):
    user_id = get_jwt_identity()

    event = Event.query.filter_by(id=event_id).with_for_update().first()

    if not event:
        return jsonify({"message": "Event not found"}), 404

    if Registration.query.filter_by(user_id=user_id, event_id=event_id).first():
        return jsonify({"message": "Already registered"}), 400

    registration = Registration(user_id=user_id, event_id=event_id)
    db.session.add(registration)
    db.session.commit()

    return jsonify({"message": "Registered successfully"}), 201


@bp.route("/events/<int:event_id>/unregister", methods=["DELETE"])
@jwt_required()
def unregister_from_event(event_id):
    user_id = get_jwt_identity()

    registration = (
        Registration.query.filter_by(user_id=user_id, event_id=event_id)
        .with_for_update()
        .first()
    )

    if not registration:
        return jsonify({"message": "Not registered"}), 404

    db.session.delete(registration)
    db.session.commit()

    return jsonify({"message": "Unregistered successfully"}), 200


@bp.route("/me/events", methods=["GET"])
@jwt_required()
def get_my_events():
    user_id = get_jwt_identity()
    registrations = Registration.query.filter_by(user_id=user_id).all()

    events = [
        {
            "id": reg.event.id,
            "title": reg.event.title,
            "description": reg.event.description,
            "date": reg.event.date.isoformat(),
            "channel": reg.event.channel,
            "language": reg.event.language,
            "location": reg.event.location,
            "status": reg.event.status,
            "group_size": reg.event.group_size,
            "num_instructors_needed": reg.event.num_instructors_needed,
            "num_representatives_needed": reg.event.num_representatives_needed,
        }
        for reg in registrations
    ]

    return jsonify(events=events), 200
