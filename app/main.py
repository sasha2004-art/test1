from flask import Flask, request, jsonify, render_template
from services.quest_generator import create_quest_from_setting

# ИЗМЕНЕНИЕ: Явно указываем пути к папкам templates и static
app = Flask(__name__, template_folder='templates', static_folder='static')


# Этот эндпоинт теперь должен рендерить HTML
@app.route("/")
def index():
    return render_template("index.html")


# Этот эндпоинт остается без изменений
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