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


def test_openai_model_missing(client, monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    from app.routes import ask as ask_module

    called = {"value": False}

    def fake_get_client():
        called["value"] = True
        raise AssertionError("_get_openai_client should not be called")

    monkeypatch.setattr(ask_module, "_get_openai_client", fake_get_client)

    payload = {
        "question": "What is the capital of France?",
        "structure": {
            "type": "object",
            "properties": {"answer": {"type": "string"}},
            "required": ["answer"],
        },
    }

    response = client.post("/api/ask", json=payload)

    assert response.status_code == 500
    assert response.get_json() == {"error": "OPENAI_MODEL is not configured"}
    assert called["value"] is False
