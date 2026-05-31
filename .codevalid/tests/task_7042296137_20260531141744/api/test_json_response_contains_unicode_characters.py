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


def test_json_response_contains_unicode_characters(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_create = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"answer": "こんにちは"}')
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

    monkeypatch.setattr(ask_module, "_get_openai_client", Mock(return_value=mock_client))

    payload = {
        "question": "How do you say hello in Japanese?",
        "structure": {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
        },
    }

    response = client.post("/api/ask", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"answer": "こんにちは"}
    assert "こんにちは" in response.get_data(as_text=True)
