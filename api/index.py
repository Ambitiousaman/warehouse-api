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
    'C1_L1': 3,
    'C2_L1': 2,
    'C3_L1': 3,
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

def calculate_cost_per_distance(weight):
    base_weight = min(weight, 5)
    extra_weight = max(0, weight - 5)
    return (base_weight * 10) + (extra_weight * 8)

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        order = request.get_json()
        
        # Calculate weights per center
        center_weights = {'C1': 0, 'C2': 0, 'C3': 0}
        for product, quantity in order.items():
            weight = PRODUCT_WEIGHTS[product] * quantity
            center = PRODUCT_LOCATIONS[product]
            center_weights[center] += weight

        # Get active centers
        active_centers = [c for c, w in center_weights.items() if w > 0]
        
        min_cost = float('inf')
        
        # Try each center as starting point
        for start_center in active_centers:
            total_weight = sum(center_weights.values())
            current_cost = 0
            
            # Cost from start center to L1
            current_cost += calculate_cost_per_distance(center_weights[start_center]) * DISTANCES[f'{start_center}_L1']
            
            remaining_centers = [c for c in active_centers if c != start_center]
            
            # Add costs for other centers
            for next_center in remaining_centers:
                # Cost to go to next center
                between_distance = DISTANCES.get(f'{start_center}_{next_center}', DISTANCES.get(f'{next_center}_{start_center}'))
                current_cost += calculate_cost_per_distance(center_weights[next_center]) * between_distance
                # Cost to deliver to L1
                current_cost += calculate_cost_per_distance(center_weights[next_center]) * DISTANCES[f'{next_center}_L1']
            
            min_cost = min(min_cost, current_cost)

        return jsonify({"minimum_cost": round(min_cost)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run()   