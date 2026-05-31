import pytest
from app import create_app, db
from app.models import Event, Task


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_happy_path_valid_event.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_happy_path_valid_event(client, app):
    with app.app_context():
        event = Event(name="KART Sprint Finals", description="Championship event")
        db.session.add(event)
        db.session.commit()

        task_1 = Task(
            title="Task 1",
            description="Do something",
            status="pending",
            event_id=event.id,
        )
        task_2 = Task(
            title="Task 2",
            description="Do something else",
            status="in_progress",
            event_id=event.id,
        )
        db.session.add_all([task_1, task_2])
        db.session.commit()
        event_id = event.id

    response = client.get(f"/api/events/{event_id}/tasks")

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert len(payload) == 2

    first = payload[0]
    second = payload[1]

    assert first["id"] == 1
    assert first["title"] == "Task 1"
    assert first["description"] == "Do something"
    assert first["status"] == "pending"
    assert first["event_id"] == event_id
    assert isinstance(first["created_at"], str)
    assert "T" in first["created_at"]
    assert isinstance(first["updated_at"], str)
    assert "T" in first["updated_at"]

    assert second["id"] == 2
    assert second["title"] == "Task 2"
    assert second["description"] == "Do something else"
    assert second["status"] == "in_progress"
    assert second["event_id"] == event_id
    assert isinstance(second["created_at"], str)
    assert "T" in second["created_at"]
    assert isinstance(second["updated_at"], str)
    assert "T" in second["updated_at"]
