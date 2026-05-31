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


def test_missing_question_field(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    from app.routes import ask as ask_module

    called = {"value": False}

    def fake_get_client():
        called["value"] = True
        raise AssertionError("_get_openai_client should not be called")

    monkeypatch.setattr(ask_module, "_get_openai_client", fake_get_client)

    response = client.post(
        "/api/ask",
        json={
            "structure": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "question is required"}
    assert called["value"] is False
