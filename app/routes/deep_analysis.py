from flask import Blueprint, jsonify, request

from app.services.deep_analysis import run_deep_analysis

deep_analysis_bp = Blueprint("deep_analysis", __name__)


@deep_analysis_bp.route("", methods=["POST"])
def deep_analysis():
    data = request.get_json(silent=True) or {}
    question = data.get("question")

    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        result = run_deep_analysis(question)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        return jsonify({"error": f"Deep analysis failed: {exc}"}), 502

    return jsonify(result)
