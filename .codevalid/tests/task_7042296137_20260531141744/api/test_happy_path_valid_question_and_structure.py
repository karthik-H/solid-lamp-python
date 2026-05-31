import json
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



def test_happy_path_valid_question_and_structure(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = _openai_response(
        '{"answer": "Paris"}'
    )

    get_client = Mock(return_value=mock_client)
    monkeypatch.setattr("app.routes.ask._get_openai_client", get_client)

    response = client.post(
        "/api/ask",
        json={
            "question": "What is the capital of France?",
            "structure": SCHEMA,
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {"answer": "Paris"}

    get_client.assert_called_once_with()
    mock_client.chat.completions.create.assert_called_once()

    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["messages"][0]["role"] == "system"
    assert "Respond only with JSON" in kwargs["messages"][0]["content"]
    assert kwargs["messages"][1] == {
        "role": "user",
        "content": "What is the capital of France?",
    }
    assert kwargs["response_format"] == {
        "type": "json_schema",
        "json_schema": {
            "name": "answer",
            "strict": True,
            "schema": SCHEMA,
        },
    }
