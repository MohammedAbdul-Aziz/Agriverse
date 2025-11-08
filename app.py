from flask import Flask, request, jsonify
from flask_cors import CORS
import yield_calculator  # This imports your other file

# Create the Flask app
app = Flask(__name__)
CORS(app)  # This allows your frontend to call the backend

# Define an API "endpoint"
# This is the URL your frontend will call
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
    # You can change host='0.0.0.0' to make it accessible on your network
    app.run(debug=True, port=5000)