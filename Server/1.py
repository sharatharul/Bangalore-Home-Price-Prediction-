from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS globally

@app.route('/predict_home_price', methods=['POST'])
def predict_home_price():
    return jsonify({'estimated_price': 100000})  # Test response

if __name__ == '__main__':
    app.run(debug=True)
