from flask import Flask, request, jsonify
from warehouse_config import warehouses

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Warehouse API",
        "endpoints": {
            "welcome": "/welcome",
            "calculate-cost": "/calculate-cost"
        }
    })

@app.route('/welcome')
def welcome():
    return jsonify({
        "message": "Welcome to the Warehouse Delivery Cost Calculator API"
    })

@app.route('/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        data = request.get_json()
        source = data.get('source_warehouse')
        destination = data.get('destination')
        weight = float(data.get('weight'))

        if not all([source, destination, weight]):
            return jsonify({"error": "Missing required fields"}), 400

        if source not in warehouses:
            return jsonify({"error": "Invalid source warehouse"}), 400

        # Your cost calculation logic here
        base_cost = 100  # Example base cost
        distance_cost = 10  # Example distance cost per km
        weight_cost = weight * 2  # Example weight cost calculation

        total_cost = base_cost + distance_cost + weight_cost

        return jsonify({
            "cost": total_cost,
            "currency": "USD"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()