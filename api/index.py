from flask import Flask, jsonify, request
from typing import Dict, Any

app = Flask(__name__)

# Constants
PRODUCT_WEIGHTS: Dict[str, float] = {
    'A': 3, 'B': 2, 'C': 8,
    'D': 12, 'E': 25, 'F': 15,
    'G': 0.5, 'H': 1, 'I': 2
}

DISTANCES: Dict[str, Any] = {
    'C1': {'L1': 3},
    'C2': {'L1': 2},
    'C3': {'L1': 3},
    'C1_C2': 4,
    'C1_C3': 2.5,
    'C2_C3': 3
}

PRODUCT_LOCATIONS: Dict[str, str] = {
    'A': 'C1', 'B': 'C1', 'C': 'C1',
    'D': 'C2', 'E': 'C2', 'F': 'C2',
    'G': 'C3', 'H': 'C3', 'I': 'C3'
}

def validate_order(order: Dict[str, int]) -> tuple[bool, str]:
    """Validate the order data"""
    if not order:
        return False, "Order cannot be empty"
    
    for product, quantity in order.items():
        if product not in PRODUCT_WEIGHTS:
            return False, f"Invalid product: {product}"
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return False, f"Invalid quantity for product {product}"
    
    return True, ""

def calculate_cost_for_weight_and_distance(weight: float, distance: float) -> float:
    """Calculate delivery cost based on weight and distance"""
    if weight <= 0 or distance <= 0:
        raise ValueError("Weight and distance must be positive")
    
    if weight <= 5:
        return weight * 10 * distance
    else:
        base_cost = 5 * 10 * distance  # First 5 kg at 10 per unit
        extra_cost = (weight - 5) * 8 * distance  # Remaining at 8 per unit
        return base_cost + extra_cost

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        order = request.get_json()
        
        # Validate order
        is_valid, error_message = validate_order(order)
        if not is_valid:
            return jsonify({"error": error_message}), 400

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
            return jsonify({
                "minimum_cost": round(total_cost),
                "centers_used": active_centers
            })

        # Try all possible routes
        min_cost = float('inf')
        
        # Try each center as starting point
        for start in active_centers:
            current_weight = center_weights[start]
            route_cost = calculate_cost_for_weight_and_distance(
                current_weight,
                DISTANCES[start]['L1']
            )
            
            remaining_centers = [c for c in active_centers if c != start]
            for next_center in remaining_centers:
                between_distance = DISTANCES.get(
                    f'{start}_{next_center}', 
                    DISTANCES.get(f'{next_center}_{start}')
                )
                route_cost += calculate_cost_for_weight_and_distance(
                    center_weights[next_center],
                    between_distance + DISTANCES[next_center]['L1']
                )
            
            min_cost = min(min_cost, route_cost)

        return jsonify({
            "minimum_cost": round(min_cost),
            "centers_used": active_centers
        })

    except KeyError as e:
        return jsonify({"error": f"Invalid product or center: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def home():
    return jsonify({
        "message": "Warehouse Cost Calculator API",
        "version": "1.0",
        "endpoints": {
            "calculate_cost": {
                "url": "/api/calculate-cost",
                "method": "POST",
                "description": "Calculate minimum delivery cost for given products"
            }
        },
        "supported_products": list(PRODUCT_WEIGHTS.keys())
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)