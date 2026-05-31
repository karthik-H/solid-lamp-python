from datetime import datetime

from flask import Blueprint, jsonify, request

from app import db
from app.models import Event

events_bp = Blueprint("events", __name__)


def _parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@events_bp.route("", methods=["GET"])
def list_events():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return jsonify([event.to_dict() for event in events])


@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    include_tasks = request.args.get("include_tasks", "false").lower() == "true"
    return jsonify(event.to_dict(include_tasks=include_tasks))


@events_bp.route("", methods=["POST"])
def create_event():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    event = Event(
        name="",
        description=data.get("description"),
        location=data.get("location"),
        start_at=_parse_datetime(data.get("start_at")),
        end_at=_parse_datetime(data.get("end_at")),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@events_bp.route("/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        if not data["name"]:
            return jsonify({"error": "name cannot be empty"}), 400
        event.name = data["name"]
    if "description" in data:
        event.description = data["description"]
    if "location" in data:
        event.location = data["location"]
    if "start_at" in data:
        event.start_at = _parse_datetime(data["start_at"])
    if "end_at" in data:
        event.end_at = _parse_datetime(data["end_at"])

    db.session.commit()
    return jsonify(event.to_dict())


@events_bp.route("/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    db.session.delete(event)
    db.session.commit()
    return "", 204


@events_bp.route("/<int:event_id>/tasks", methods=["GET"])
def list_event_tasks(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify([task.to_dict() for task in event.tasks])
