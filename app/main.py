import os
import logging
from flask import Flask, request, jsonify, render_template
from services.quest_generator import create_quest_from_setting

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


@app.route("/generate", methods=["POST"])
def generate_quest_endpoint():
    data = request.get_json()
    if not data or "setting" not in data or "api_key" not in data:
        return (
            jsonify({"error": "Missing 'setting' or 'api_key' in request body"}),
            400,
        )

    setting = data["setting"]
    api_key = data["api_key"]

    quest_json = create_quest_from_setting(setting, api_key)

    if "error" in quest_json:
        return jsonify(quest_json), 500

    return jsonify(quest_json)
