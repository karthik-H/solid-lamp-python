import pytest
from app import create_app, db
from app.models import Event


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_empty_name_field.db"
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


def test_empty_name_field(client, app):
    with app.app_context():
        event = Event(name="KART Original", description="Desc", location="Loc")
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.put(f"/api/events/{event_id}", json={"name": ""})

    assert response.status_code == 400
    assert response.get_json() == {"error": "name cannot be empty"}

    with app.app_context():
        unchanged = db.session.get(Event, event_id)
        assert unchanged.name == "KART Original"
