from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        }
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_happy_path_valid_question_and_structure(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_create = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"answer": "Paris"}')
                )
            ]
        )
    )
    mock_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=mock_create)
        )
    )

    from app.routes import ask as ask_module

    get_client_mock = Mock(return_value=mock_client)
    monkeypatch.setattr(ask_module, "_get_openai_client", get_client_mock)

    payload = {
        "question": "What is the capital of France?",
        "structure": {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
        },
    }

    response = client.post("/api/ask", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"answer": "Paris"}

    get_client_mock.assert_called_once_with()
    mock_create.assert_called_once()
    kwargs = mock_create.call_args.kwargs
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["messages"][1] == {
        "role": "user",
        "content": "What is the capital of France?",
    }
    assert kwargs["response_format"] == {
        "type": "json_schema",
        "json_schema": {
            "name": "answer",
            "strict": True,
            "schema": payload["structure"],
        },
    }
