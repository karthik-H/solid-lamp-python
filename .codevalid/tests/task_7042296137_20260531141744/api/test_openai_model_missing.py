from unittest.mock import Mock

import pytest

from app import create_app


SCHEMA = {
    "type": "object",
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
}


@pytest.fixture()
def app():
    return create_app({"TESTING": True})


@pytest.fixture()
def client(app):
    return app.test_client()



def test_openai_model_missing(client, monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    get_client = Mock()
    monkeypatch.setattr("app.routes.ask._get_openai_client", get_client)

    response = client.post(
        "/api/ask",
        json={"question": "What is the capital of France?", "structure": SCHEMA},
    )

    assert response.status_code == 500
    assert response.get_json() == {"error": "OPENAI_MODEL is not configured"}
    get_client.assert_not_called()
