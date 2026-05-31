import pytest
from app import create_app, db
from app.models import Event


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_happy_path_valid_update.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"check_same_thread": False}},
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_happy_path_valid_update(client, app):
    with app.app_context():
        event = Event(
            name="Old Event",
            description="Old desc",
            location="Old loc",
            start_at=None,
            end_at=None,
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    payload = {
        "name": "KART New Event",
        "description": "New desc",
        "location": "New loc",
        "start_at": "2024-02-01T00:00:00",
        "end_at": "2024-02-02T00:00:00",
    }

    response = client.put(f"/api/events/{event_id}", json=payload)

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == event_id
    assert body["name"] == "KART New Event"
    assert body["description"] == "New desc"
    assert body["location"] == "New loc"
    assert body["start_at"] == "2024-02-01T00:00:00"
    assert body["end_at"] == "2024-02-02T00:00:00"
    assert "created_at" in body
    assert "updated_at" in body

    with app.app_context():
        updated = db.session.get(Event, event_id)
        assert updated.name == "KART New Event"
        assert updated.description == "New desc"
        assert updated.location == "New loc"
        assert updated.start_at.isoformat() == "2024-02-01T00:00:00"
        assert updated.end_at.isoformat() == "2024-02-02T00:00:00"
