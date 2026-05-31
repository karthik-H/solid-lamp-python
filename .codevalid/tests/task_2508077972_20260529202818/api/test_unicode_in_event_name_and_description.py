from pathlib import Path

import pytest
from app import create_app


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "unicode_in_event_name_and_description.sqlite"
    app = create_app(
        {
            "TESTING": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        }
    )
    with app.test_client() as test_client:
        yield test_client


def test_unicode_in_event_name_and_description(client):
    payload = {
        "name": "KART café",
        "description": "Journée d'événement",
    }

    response = client.post("/api/events", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] >= 1
    assert body["name"] == "KART café"
    assert body["description"] == "Journée d'événement"
    assert body["location"] is None
    assert body["start_at"] is None
    assert body["end_at"] is None

    fetch_response = client.get(f"/api/events/{body['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.get_json()
    assert fetched["name"] == "KART café"
    assert fetched["description"] == "Journée d'événement"
