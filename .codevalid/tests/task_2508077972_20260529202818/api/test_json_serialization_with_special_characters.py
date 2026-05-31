import json
import pytest
from app import create_app, db
from app.models import Event, Task


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test_json_serialization_with_special_characters.db"
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


def test_json_serialization_with_special_characters(client, app):
    special_title = 'Meeting with caf\u00e9 & "team"'
    special_description = 'Newline\nand tab\t'
    special_status = '\u2705 done'

    with app.app_context():
        event = Event(name="KART Unicode Event")
        db.session.add(event)
        db.session.commit()

        task = Task(
            title=special_title,
            description=special_description,
            status=special_status,
            event_id=event.id,
        )
        db.session.add(task)
        db.session.commit()
        event_id = event.id

    response = client.get(f"/api/events/{event_id}/tasks")

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert len(payload) == 1

    item = payload[0]
    assert item["title"] == special_title
    assert item["description"] == special_description
    assert item["status"] == special_status
    assert item["event_id"] == event_id

    raw_text = response.get_data(as_text=True)
    parsed_again = json.loads(raw_text)
    assert parsed_again[0]["title"] == special_title
    assert parsed_again[0]["description"] == special_description
    assert parsed_again[0]["status"] == special_status
    assert '\\n' in raw_text
    assert '\\t' in raw_text
    assert '\\"team\\"' in raw_text
