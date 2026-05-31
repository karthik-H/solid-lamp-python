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


def test_json_response_escapes_control_characters(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    value = "Item 1\tItem 2\nItem 3"
    mock_create = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"answer": "Item 1\\tItem 2\\nItem 3"}'
                    )
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
        "question": "Describe a tab-delimited list",
        "structure": {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
        },
    }

    response = client.post("/api/ask", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"answer": value}

    raw_body = response.get_data(as_text=True)
    assert "\\t" in raw_body
    assert "\\n" in raw_body
