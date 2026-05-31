import pytest
from app import create_app, db
from app.models import Event


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_special_characters_in_response.db"
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


def test_special_characters_in_response(client, app):
    special_description = 'Café ☕ "special" <script>'

    with app.app_context():
        event = Event(name="KART Test", description=special_description, location="Loc")
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.put(f"/api/events/{event_id}", json={})

    assert response.status_code == 200
    body = response.get_json()
    assert body["description"] == special_description
    assert "special" in response.get_data(as_text=True)
