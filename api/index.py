from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API Flask funcionando na Vercel!"})

@app.route("/hello", methods=["POST"])
def hello():
    data = request.get_json()
    return jsonify({"message": f"Olá, {data.get('nome', 'sem nome')}!"})
