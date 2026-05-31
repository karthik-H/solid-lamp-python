from types import SimpleNamespace
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



def _openai_response(content: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )



def test_openai_returns_invalid_json(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    raw_content = "This is text, not JSON"
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = _openai_response(raw_content)

    get_client = Mock(return_value=mock_client)
    monkeypatch.setattr("app.routes.ask._get_openai_client", get_client)

    response = client.post(
        "/api/ask",
        json={"question": "What is the capital of France?", "structure": SCHEMA},
    )

    assert response.status_code == 502
    assert response.get_json() == {
        "error": "OpenAI returned invalid JSON",
        "raw": raw_content,
    }
