import pytest

from app import create_app, db
from app.models import Event


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "events.sqlite"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_not_found_event_does_not_exist(client, app):
    with app.app_context():
        existing_event = Event(name="KART Existing Event")
        db.session.add(existing_event)
        db.session.commit()
        existing_event_id = existing_event.id

    response = client.delete("/api/events/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Event not found"}

    with app.app_context():
        assert db.session.get(Event, existing_event_id) is not None
        assert Event.query.count() == 1
