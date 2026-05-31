import pytest
from app import create_app, db


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_not_found_event_id.db"
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


def test_not_found_event_id(client):
    response = client.put("/api/events/999", json={"name": "KART Missing"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Event not found"}
