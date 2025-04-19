from flask import Flask, request, jsonify
from flask_cors import CORS
from .warehouse_config import WAREHOUSES, DISTANCES

app = Flask(__name__)
CORS(app)

# Your existing route handlers and functions here...

# This is crucial for Vercel
app = app.wsgi_app