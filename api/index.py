from flask import Flask, request, jsonify
from flask_cors import CORS
from .warehouse_config import WAREHOUSES, DISTANCES

app = Flask(__name__)
CORS(app)

def validate_input(data):
    errors = []
    if 'source' not in data:
        errors.append("Source warehouse is required")
    elif data['source'] not in WAREHOUSES:
        errors.append(f"Invalid source warehouse: {data['source']}. Valid warehouses are: C1, C2, C3")
    
    if 'weight' not in data:
        errors.append("Weight is required")
    elif not isinstance(data['weight'], (int, float)):
        errors.append("Weight must be a number")
    elif data['weight'] <= 0:
        errors.append("Weight must be greater than 0")
    
    valid_destinations = ['L1', 'C1', 'C2', 'C3']
    if 'destination' in data and data['destination'] not in valid_destinations:
        errors.append(f"Invalid destination: {data['destination']}. Valid destinations are: {', '.join(valid_destinations)}")
    
    return errors

def get_distance(start, end):
    if (start, end) in DISTANCES:
        return DISTANCES[(start, end)]
    if (end, start) in DISTANCES:
        return DISTANCES[(end, start)]
    return None

def calculate_delivery_cost(data):
    errors = validate_input(data)
    if errors:
        raise ValueError({"errors": errors})
    
    source = data['source']
    destination = data.get('destination', 'L1')
    weight = data['weight']
    
    distance = get_distance(source, destination)
    if distance is None:
        raise ValueError({"errors": [f"No valid route found between {source} and {destination}"]})
    
    base_cost = weight * 10
    distance_cost = distance * weight * 0.5
    total_cost = base_cost + distance_cost
    
    return {
        'total_cost': round(total_cost, 2),
        'base_cost': round(base_cost, 2),
        'distance_cost': round(distance_cost, 2),
        'route': f'{source} -> {destination}',
        'distance': distance
    }

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON',
                'example_format': {
                    'source': 'C1',
                    'destination': 'L1',
                    'weight': 100
                }
            }), 400
        
        data = request.get_json()
        result = calculate_delivery_cost(data)
        return jsonify({'result': result})
    
    except ValueError as e:
        error_dict = e.args[0] if isinstance(e.args[0], dict) else {'errors': [str(e)]}
        return jsonify(error_dict), 400
    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'message': str(e)
        }), 500

@app.route('/api', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to Warehouse Delivery Cost Calculator API',
        'usage': {
            'endpoint': '/api/calculate-cost',
            'method': 'POST',
            'body_format': {
                'source': 'Warehouse ID (C1, C2, or C3)',
                'destination': 'Delivery location (default: L1)',
                'weight': 'Weight of the package in units'
            }
        }
    })

# Required for Vercel
app = app.wsgi_app