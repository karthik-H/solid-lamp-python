import json
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
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    question = "What is the capital of France?"
    structure = {
        "type": "object",
        "properties": {"capital": {"type": "string"}},
        "required": ["capital"],
    }

    create_mock = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps({"capital": "Paris"}))
                )
            ]
        )
    )
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create_mock))
    )

    import app.routes.ask as ask_module

    get_client_mock = Mock(return_value=fake_client)
    monkeypatch.setattr(ask_module, "_get_openai_client", get_client_mock)

    response = client.post(
        "/api/ask",
        json={"question": question, "structure": structure},
    )

    assert response.status_code == 200
    assert response.get_json() == {"capital": "Paris"}

    get_client_mock.assert_called_once_with()
    create_mock.assert_called_once()

    kwargs = create_mock.call_args.kwargs
    assert kwargs["model"] == "gpt-4o-mini"
    assert kwargs["messages"][1]["role"] == "user"
    assert kwargs["messages"][1]["content"] == question
    assert kwargs["response_format"] == {
        "type": "json_schema",
        "json_schema": {
            "name": "answer",
            "strict": True,
            "schema": structure,
        },
    }
