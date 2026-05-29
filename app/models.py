from datetime import datetime, timezone

from app import db


def _utc_now():
    return datetime.now(timezone.utc)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    start_at = db.Column(db.DateTime, nullable=True)
    end_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_utc_now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=_utc_now, onupdate=_utc_now
    )

    tasks = db.relationship(
        "Task", back_populates="event", cascade="all, delete-orphan"
    )

    def to_dict(self, include_tasks=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "start_at": self.start_at.isoformat() if self.start_at else None,
            "end_at": self.end_at.isoformat() if self.end_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_tasks:
            data["tasks"] = [task.to_dict() for task in self.tasks]
        return data


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pending")
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=_utc_now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=_utc_now, onupdate=_utc_now
    )

    event = db.relationship("Event", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "event_id": self.event_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
