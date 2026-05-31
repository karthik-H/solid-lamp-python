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



def test_openai_api_key_missing(client, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/api/ask",
        json={"question": "What is the capital of France?", "structure": SCHEMA},
    )

    assert response.status_code == 500
    assert response.get_json() == {"error": "OPENAI_API_KEY is not configured"}
