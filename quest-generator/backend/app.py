# quest-generator/backend/app.py

from flask import Flask, request, jsonify
from quest_logic.generator import create_quest_from_setting

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, QuestGenerator!"


@app.route("/generate", methods=["POST"])
def generate_quest_endpoint():
    data = request.get_json()
    if not data or "setting" not in data or "api_key" not in data:
        return (
            jsonify(
                {"error": "Missing 'setting' or 'api_key' in request body"}
            ),
            400,
        )

    setting = data["setting"]
    api_key = data["api_key"]

    quest_json = create_quest_from_setting(setting, api_key)

    if "error" in quest_json:
        return jsonify(quest_json), 500

    return jsonify(quest_json)
