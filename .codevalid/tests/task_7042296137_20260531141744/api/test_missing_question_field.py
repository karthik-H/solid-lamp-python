from unittest.mock import Mock

import pytest

from app import create_app


@pytest.fixture()
def app():
    return create_app({"TESTING": True})


@pytest.fixture()
def client(app):
    return app.test_client()



def test_missing_question_field(client, monkeypatch):
    get_client = Mock()
    monkeypatch.setattr("app.routes.ask._get_openai_client", get_client)

    response = client.post(
        "/api/ask",
        json={
            "structure": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "question is required"}
    get_client.assert_not_called()
