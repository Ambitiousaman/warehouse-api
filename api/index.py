from flask import Flask, jsonify, request

app = Flask(__name__)

# Product weights (in kg)
PRODUCT_WEIGHTS = {
    'A': 3, 'B': 2, 'C': 8,
    'D': 12, 'E': 25, 'F': 15,
    'G': 0.5, 'H': 1, 'I': 2
}

# Center locations and distances
DISTANCES = {
    'C1': {'L1': 3},
    'C2': {'L1': 2},
    'C3': {'L1': 3},
    'C1_C2': 4,
    'C1_C3': 2.5,
    'C2_C3': 3
}

# Product locations
PRODUCT_LOCATIONS = {
    'A': 'C1', 'B': 'C1', 'C': 'C1',
    'D': 'C2', 'E': 'C2', 'F': 'C2',
    'G': 'C3', 'H': 'C3', 'I': 'C3'
}

def calculate_delivery_cost(total_weight, distance):
    base_cost = min(total_weight, 5) * 10 * distance
    if total_weight > 5:
        additional_weight = total_weight - 5
        additional_cost = additional_weight * 8 * distance
        return base_cost + additional_cost
    return base_cost

@app.route('/')
def home():
    return jsonify({
        "message": "Warehouse Cost Calculator API",
        "endpoints": {
            "calculate_cost": "/api/calculate-cost"
        }
    })

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        order = request.get_json()
        if not order:
            return jsonify({"error": "No order data provided"}), 400
        
        # Calculate total weight and group products by center
        center_weights = {'C1': 0, 'C2': 0, 'C3': 0}
        total_weight = 0
        
        for product, quantity in order.items():
            if product not in PRODUCT_WEIGHTS:
                return jsonify({"error": f"Invalid product: {product}"}), 400
            if not isinstance(quantity, (int, float)) or quantity < 0:
                return jsonify({"error": f"Invalid quantity for product {product}"}), 400
            
            weight = PRODUCT_WEIGHTS[product] * quantity
            center = PRODUCT_LOCATIONS[product]
            center_weights[center] += weight
            total_weight += weight

        # Calculate minimum cost for different routing possibilities
        min_cost = float('inf')
        
        # Direct delivery from each center if it has all products
        for center, weight in center_weights.items():
            if weight == total_weight:
                cost = calculate_delivery_cost(weight, DISTANCES[center]['L1'])
                min_cost = min(min_cost, cost)

        # Calculate costs for different routing combinations
        centers_with_products = [c for c, w in center_weights.items() if w > 0]
        
        if len(centers_with_products) > 1:
            # Try all possible routes starting from each center
            for start_center in centers_with_products:
                route_cost = 0
                remaining_weight = total_weight
                
                # Cost to deliver from start center to L1
                route_cost += calculate_delivery_cost(
                    center_weights[start_center],
                    DISTANCES[start_center]['L1']
                )
                remaining_weight -= center_weights[start_center]
                
                # Add costs for picking up from other centers
                for other_center in centers_with_products:
                    if other_center != start_center:
                        center_distance = DISTANCES.get(
                            f"{start_center}_{other_center}",
                            DISTANCES.get(f"{other_center}_{start_center}")
                        )
                        if center_distance:
                            route_cost += calculate_delivery_cost(
                                remaining_weight,
                                center_distance
                            )
                            remaining_weight -= center_weights[other_center]
                            route_cost += calculate_delivery_cost(
                                remaining_weight,
                                DISTANCES[other_center]['L1']
                            )
                
                min_cost = min(min_cost, route_cost)

        return jsonify({"minimum_cost": round(min_cost)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Add error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)