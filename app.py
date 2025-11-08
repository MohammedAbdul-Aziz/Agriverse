from flask import Flask, request, jsonify
from flask_cors import CORS
import yield_calculator

# Create the Flask app
app = Flask(__name__)
CORS(app)

# 1. NEW: Default GET route for the root URL
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "API is running", "endpoint": "Use POST /calculate"})

# 2. Existing POST route for the calculator
@app.route('/calculate', methods=['POST'])
def handle_calculation():
    # 1. Get the JSON data sent by the frontend
    data = request.json
    
    # 2. Call your logic function from the other file
    result = yield_calculator.calculate_yield(data)
    
    # 3. Return the result as JSON to the frontend
    return jsonify(result)

# This runs the server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
