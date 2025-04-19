from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Warehouse locations and their internal distances
WAREHOUSES = {
    'C1': {'A': 3, 'B': 2, 'C': 8},
    'C2': {'D': 12, 'E': 25, 'F': 15},
    'C3': {'G': 0.5, 'H': 1, 'I': 2}
}

# Distances between warehouses and delivery location
DISTANCES = {
    ('C1', 'L1'): 3,
    ('C2', 'L1'): 2.5,
    ('C3', 'L1'): 2,
    ('C1', 'C2'): 4,
    ('C2', 'C3'): 3,
    ('C1', 'C3'): 5
}

@app.route('/api', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to Warehouse Delivery Cost Calculator API'
    })

@app.route('/api/calculate-cost', methods=['POST'])
def calculate_cost():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        source = data.get('source')
        destination = data.get('destination', 'L1')
        weight = data.get('weight')
        
        if not all([source, weight]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        if source not in WAREHOUSES:
            return jsonify({'error': f'Invalid source warehouse: {source}'}), 400
            
        # Calculate cost
        distance = DISTANCES.get((source, destination)) or DISTANCES.get((destination, source))
        if not distance:
            return jsonify({'error': f'No route found between {source} and {destination}'}), 400
            
        base_cost = float(weight) * 10
        distance_cost = distance * float(weight) * 0.5
        total_cost = base_cost + distance_cost
        
        return jsonify({
            'total_cost': round(total_cost, 2),
            'base_cost': round(base_cost, 2),
            'distance_cost': round(distance_cost, 2),
            'route': f'{source} -> {destination}',
            'distance': distance
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel Serverless
app = app.wsgi_app