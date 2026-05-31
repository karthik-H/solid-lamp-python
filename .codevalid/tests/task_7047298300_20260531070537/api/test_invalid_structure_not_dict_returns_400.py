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


def test_invalid_structure_not_dict_returns_400(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    import app.routes.ask as ask_module

    get_client_mock = Mock()
    monkeypatch.setattr(ask_module, "_get_openai_client", get_client_mock)

    response = client.post(
        "/api/ask",
        json={"question": "Who wrote Hamlet?", "structure": "not a dict"},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "structure must be a JSON Schema object"
    }
    get_client_mock.assert_not_called()
