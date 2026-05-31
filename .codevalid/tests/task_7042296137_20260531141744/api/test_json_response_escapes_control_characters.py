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



def test_json_response_escapes_control_characters(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = _openai_response(
        '{"answer": "Item 1\\tItem 2\\nItem 3"}'
    )

    get_client = Mock(return_value=mock_client)
    monkeypatch.setattr("app.routes.ask._get_openai_client", get_client)

    response = client.post(
        "/api/ask",
        json={
            "question": "Describe a tab-delimited list",
            "structure": SCHEMA,
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {"answer": "Item 1\tItem 2\nItem 3"}

    raw_body = response.get_data(as_text=True)
    assert "\\t" in raw_body
    assert "\\n" in raw_body
