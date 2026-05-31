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



def test_openai_request_fails_network_error(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = ConnectionError("network down")

    get_client = Mock(return_value=mock_client)
    monkeypatch.setattr("app.routes.ask._get_openai_client", get_client)

    response = client.post(
        "/api/ask",
        json={"question": "What is the capital of France?", "structure": SCHEMA},
    )

    assert response.status_code == 502
    assert response.get_json() == {"error": "OpenAI request failed: network down"}
    get_client.assert_called_once_with()
    mock_client.chat.completions.create.assert_called_once()
