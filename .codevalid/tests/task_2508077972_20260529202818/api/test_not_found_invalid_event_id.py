import pytest
from app import create_app, db


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_not_found_invalid_event_id.db"
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


def test_not_found_invalid_event_id(client):
    response = client.get("/api/events/999/tasks")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Event not found"}
