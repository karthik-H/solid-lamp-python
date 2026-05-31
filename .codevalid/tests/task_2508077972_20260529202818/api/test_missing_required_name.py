from pathlib import Path

import pytest
from app import create_app


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "missing_required_name.sqlite"
    app = create_app(
        {
            "TESTING": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        }
    )
    with app.test_client() as test_client:
        yield test_client


def test_missing_required_name(client):
    response = client.post(
        "/api/events",
        json={"description": "No name"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "name is required"}

    list_response = client.get("/api/events")
    assert list_response.status_code == 200
    assert list_response.get_json() == []
