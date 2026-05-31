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


def test_happy_path_event_deleted(client, app):
    with app.app_context():
        event = Event(name="KART Championship")
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.delete(f"/api/events/{event_id}")

    assert response.status_code == 204
    assert response.data == b""

    with app.app_context():
        deleted_event = db.session.get(Event, event_id)
        assert deleted_event is None
        assert Event.query.count() == 0
