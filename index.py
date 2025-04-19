from flask import Flask, request, jsonify
from warehouse_config import warehouses

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Warehouse API",
        "status": "online",
        "available_endpoints": {
            "welcome": "/welcome",
            "calculate_cost": "/calculate-cost (POST)"
        }
    })

@app.route('/welcome')
def welcome():
    return jsonify({
        "message": "Welcome to the Warehouse Delivery Cost Calculator API",
        "available_warehouses": list(warehouses.keys())
    })

@app.route('/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['source_warehouse', 'destination', 'weight']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        source = data['source_warehouse']
        destination = data['destination']
        weight = float(data['weight'])

        # Validate warehouse exists
        if source not in warehouses:
            return jsonify({"error": "Invalid source warehouse"}), 400

        # Validate weight
        if weight <= 0:
            return jsonify({"error": "Weight must be greater than 0"}), 400

        # Calculate cost (example calculation)
        base_cost = 100
        weight_cost = weight * 10
        distance_factor = 1.5
        total_cost = base_cost + weight_cost * distance_factor

        return jsonify({
            "source": source,
            "destination": destination,
            "weight": weight,
            "total_cost": round(total_cost, 2),
            "currency": "USD"
        })

    except ValueError:
        return jsonify({"error": "Invalid weight format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)