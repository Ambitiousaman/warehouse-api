from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to Warehouse API",
        "status": "active"
    })

@app.route('/api', methods=['GET'])
def api():
    return jsonify({
        "message": "API is working"
    })