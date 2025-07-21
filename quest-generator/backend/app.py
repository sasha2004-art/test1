# quest-generator/backend/app.py

# Добавь render_template в импорты
from flask import Flask, request, jsonify, render_template

# Меняем импорт
from backend.quest_logic.generator import create_quest

app = Flask(__name__)


# Этот эндпоинт теперь должен рендерить HTML
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_quest_endpoint():
    data = request.get_json()
    # Добавляем проверку на model
    if not data or "setting" not in data or "model" not in data:
        return (
            jsonify({"error": "Missing 'setting' or 'model' in request body"}),
            400,
        )

    setting = data["setting"]
    model = data["model"]
    # API ключ теперь опционален
    api_key = data.get("api_key")

    quest_json = create_quest(setting, model, api_key)

    if "error" in quest_json:
        return jsonify(quest_json), 500

    return jsonify(quest_json)
