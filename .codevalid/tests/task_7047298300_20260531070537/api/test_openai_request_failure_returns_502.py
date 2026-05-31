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


def test_openai_request_failure_returns_502(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    create_mock = Mock(side_effect=Exception("network timeout"))
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create_mock))
    )

    import app.routes.ask as ask_module

    get_client_mock = Mock(return_value=fake_client)
    monkeypatch.setattr(ask_module, "_get_openai_client", get_client_mock)

    response = client.post(
        "/api/ask",
        json={
            "question": "What is the capital of France?",
            "structure": {
                "type": "object",
                "properties": {"capital": {"type": "string"}},
                "required": ["capital"],
            },
        },
    )

    assert response.status_code == 502
    assert response.get_json() == {
        "error": "OpenAI request failed: network timeout"
    }
    get_client_mock.assert_called_once_with()
    create_mock.assert_called_once()
