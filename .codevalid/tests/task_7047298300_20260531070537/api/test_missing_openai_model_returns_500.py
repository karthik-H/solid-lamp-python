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


def test_missing_openai_model_returns_500(client, monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    import app.routes.ask as ask_module

    get_client_mock = Mock()
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

    assert response.status_code == 500
    assert response.get_json() == {"error": "OPENAI_MODEL is not configured"}
    get_client_mock.assert_not_called()
