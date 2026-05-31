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



def test_json_response_contains_unicode_characters(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = _openai_response(
        '{"answer": "こんにちは"}'
    )

    get_client = Mock(return_value=mock_client)
    monkeypatch.setattr("app.routes.ask._get_openai_client", get_client)

    response = client.post(
        "/api/ask",
        json={
            "question": "How do you say hello in Japanese?",
            "structure": SCHEMA,
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {"answer": "こんにちは"}
    assert "こんにちは" in response.get_data(as_text=True)
