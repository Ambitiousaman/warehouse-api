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

def calculate_cost_for_weight_and_distance(weight, distance):
    if weight <= 5:
        return weight * 10 * distance
    else:
        base_cost = 5 * 10 * distance  # First 5 kg at 10 per unit
        extra_cost = (weight - 5) * 8 * distance  # Remaining at 8 per unit
        return base_cost + extra_cost

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        order = request.get_json()
        
        # Calculate weights for each center
        center_weights = {'C1': 0, 'C2': 0, 'C3': 0}
        for product, quantity in order.items():
            weight = PRODUCT_WEIGHTS[product] * quantity
            center = PRODUCT_LOCATIONS[product]
            center_weights[center] += weight

        # Get centers that have products
        active_centers = [c for c, w in center_weights.items() if w > 0]
        
        if not active_centers:
            return jsonify({"error": "No valid products in order"}), 400

        # If only one center has products, direct delivery
        if len(active_centers) == 1:
            center = active_centers[0]
            total_cost = calculate_cost_for_weight_and_distance(
                center_weights[center],
                DISTANCES[center]['L1']
            )
            return jsonify({"minimum_cost": round(total_cost)})

        # Try all possible routes
        min_cost = float('inf')
        
        # Try each center as starting point
        for start in active_centers:
            # Calculate direct route cost
            current_weight = center_weights[start]
            route_cost = calculate_cost_for_weight_and_distance(
                current_weight,
                DISTANCES[start]['L1']
            )
            
            # Add costs for other centers
            remaining_centers = [c for c in active_centers if c != start]
            for next_center in remaining_centers:
                # Cost to go between centers
                between_distance = DISTANCES.get(f'{start}_{next_center}', 
                                              DISTANCES.get(f'{next_center}_{start}'))
                route_cost += calculate_cost_for_weight_and_distance(
                    center_weights[next_center],
                    between_distance + DISTANCES[next_center]['L1']
                )
            
            min_cost = min(min_cost, route_cost)

        return jsonify({"minimum_cost": round(min_cost)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def home():
    return jsonify({
        "message": "Warehouse Cost Calculator API",
        "endpoints": {
            "calculate_cost": "/api/calculate-cost"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)