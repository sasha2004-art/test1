import os
from flask import Flask, request, jsonify, render_template
from .llm_integrations.factory import get_llm_instance
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate', methods=['POST'])
def generate_quest_endpoint():
    data = request.get_json()
    if not data or "setting" not in data:
        return jsonify({"error": "Missing 'setting' in request body"}), 400

    llm_type = data.get('llm_type', 'groq')
    api_key = data.get('api_key')
    setting = data['setting']

    try:
        llm_instance = get_llm_instance(
            llm_type=llm_type,
            api_key=api_key,
            model_path=os.getenv('LOCAL_MODEL_PATH')
        )
        quest_json = llm_instance.generate_quest(setting)
        return jsonify(quest_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
