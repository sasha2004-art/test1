import os
import logging
from flask import Flask, request, jsonify, render_template
from services.quest_generator import (
    create_quest_from_setting,
    validate_api_key,
    get_available_models,
)

app = Flask(__name__, template_folder="templates", static_folder="static")

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    port = os.getenv("EXTERNAL_PORT", "5001")

    app.logger.info("=" * 60)
    app.logger.info("  AI Quest Generator запущен!")
    app.logger.info(f"  Для доступа к приложению откройте: http://localhost:{port}")
    app.logger.info("=" * 60)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/generate", methods=["POST"])
def generate_quest_endpoint():
    data = request.get_json()
    if (
        not data
        or "setting" not in data
        or "api_key" not in data
        or "api_provider" not in data
        or "model" not in data
    ):
        return (
            jsonify(
                {
                    "error": "Missing 'setting', 'api_key', 'api_provider' or 'model' in request body"
                }
            ),
            400,
        )

    setting = data["setting"]
    api_key = data["api_key"]
    api_provider = data["api_provider"]
    model = data["model"]

    quest_json = create_quest_from_setting(setting, api_key, api_provider, model)

    if "error" in quest_json:
        return jsonify(quest_json), 500

    return jsonify(quest_json)


@app.route("/validate_api_key", methods=["POST"])
def validate_api_key_endpoint():
    data = request.get_json()
    if not data or "api_key" not in data or "api_provider" not in data:
        return jsonify({"error": "Missing 'api_key' or 'api_provider'"}), 400

    api_key = data["api_key"]
    api_provider = data["api_provider"]

    if not api_key:
        return jsonify({"status": "error", "message": "API ключ не может быть пустым."})

    result = validate_api_key(api_provider=api_provider, api_key=api_key)

    return jsonify(result)


@app.route("/api/models", methods=["POST"])
def available_models_endpoint():
    data = request.get_json()
    if not data or "api_key" not in data or "api_provider" not in data:
        return jsonify({"error": "Missing 'api_key' or 'api_provider'"}), 400

    api_key = data["api_key"]
    api_provider = data["api_provider"]

    if not api_key:
        return jsonify({"error": "API ключ не может быть пустым."})

    models = get_available_models(api_provider=api_provider, api_key=api_key)

    return jsonify(models)
