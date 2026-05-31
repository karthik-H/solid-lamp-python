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


def test_openai_returns_empty_response(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_create = Mock(
        return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
        )
    )
    mock_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=mock_create)
        )
    )

    from app.routes import ask as ask_module

    monkeypatch.setattr(ask_module, "_get_openai_client", Mock(return_value=mock_client))

    payload = {
        "question": "What is the capital of France?",
        "structure": {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
        },
    }

    response = client.post("/api/ask", json=payload)

    assert response.status_code == 502
    assert response.get_json() == {"error": "OpenAI returned an empty response"}
    mock_create.assert_called_once()
