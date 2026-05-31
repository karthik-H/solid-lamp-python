import json
import os

from flask import Blueprint, jsonify, request
from openai import OpenAI

ask_bp = Blueprint("ask", __name__)


def _get_openai_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    return OpenAI(api_key=api_key, base_url=base_url)


@ask_bp.route("", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    structure = data.get("structure")

    if not question:
        return jsonify({"error": "question is required"}), 400
    if not structure or not isinstance(structure, dict):
        return jsonify({"error": "structure must be a JSON Schema object"}), 400

    model = os.environ.get("OPENAI_MODEL")
    if not model:
        return jsonify({"error": "OPENAI_MODEL is not configured"}), 500

    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer the user's question. Respond only with JSON "
                        "that matches the provided schema."
                    ),
                },
                {"role": "user", "content": question},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "answer",
                    "strict": True,
                    "schema": structure,
                },
            },
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"OpenAI request failed: {exc}"}), 502

    content = response.choices[0].message.content
    if not content:
        return jsonify({"error": "OpenAI returned an empty response"}), 502

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        return jsonify({"error": "OpenAI returned invalid JSON", "raw": content}), 502

    return jsonify(result)
