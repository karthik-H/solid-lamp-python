from flask import Blueprint, jsonify, request

from app import db
from app.models import Event, Task

tasks_bp = Blueprint("tasks", __name__)

VALID_STATUSES = {"pending", "in_progress", "completed", "cancelled"}


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    query = Task.query
    event_id = request.args.get("event_id", type=int)
    if event_id is not None:
        query = query.filter_by(event_id=event_id)
    unassigned = request.args.get("unassigned", "false").lower() == "true"
    if unassigned:
        query = query.filter(Task.event_id.is_(None))
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        return jsonify(
            {"error": f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"}
        ), 400

    event_id = data.get("event_id")
    if event_id is not None:
        event = db.session.get(Event, event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404

    task = Task(
        title=title,
        description=data.get("description"),
        status=status,
        event_id=event_id,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}
    if "title" in data:
        if not data["title"]:
            return jsonify({"error": "title cannot be empty"}), 400
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify(
                {
                    "error": f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"
                }
            ), 400
        task.status = data["status"]
    if "event_id" in data:
        event_id = data["event_id"]
        if event_id is not None:
            event = db.session.get(Event, event_id)
            if not event:
                return jsonify({"error": "Event not found"}), 404
        task.event_id = event_id

    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return "", 204


@tasks_bp.route("/<int:task_id>/assign", methods=["POST"])
def assign_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    if event_id is None:
        return jsonify({"error": "event_id is required"}), 400

    event = db.session.get(Event, event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    task.event_id = event_id
    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route("/<int:task_id>/unassign", methods=["POST"])
def unassign_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.event_id = None
    db.session.commit()
    return jsonify(task.to_dict())
