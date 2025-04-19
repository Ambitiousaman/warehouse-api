from flask import Flask, request, jsonify
from warehouse_config import warehouses

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Warehouse API",
        "status": "online"
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
        weight = float(data.get('weight', 0))

        if not all([source, destination, weight]):
            return jsonify({"error": "Missing required fields"}), 400

        if source not in warehouses:
            return jsonify({"error": "Invalid source warehouse"}), 400

        # Simple cost calculation
        base_cost = 100
        weight_cost = weight * 10
        total_cost = base_cost + weight_cost

        return jsonify({
            "source": source,
            "destination": destination,
            "weight": weight,
            "total_cost": round(total_cost, 2),
            "currency": "USD"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Important: Add this for Vercel
app.debug = True

if __name__ == '__main__':
    app.run()