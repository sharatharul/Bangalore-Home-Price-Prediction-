from columns import columns
from flask import Flask,request,jsonify
from flask_cors import CORS
from joblib import load
import numpy as np
import os
import util
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import time
import traceback

# Configure logging
def setup_logger():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up file handler with rotation
    file_handler = RotatingFileHandler(
        'logs/server.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Get the logger
    logger = logging.getLogger('HomePrice')
    logger.setLevel(logging.DEBUG)
    
    # Add handlers if they haven't been added already
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logger()

# Global flag for artifact status
artifacts_loaded = False

def require_artifacts(f):
    """Decorator to check if artifacts are loaded before processing requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not artifacts_loaded:
            logger.error("Artifacts not loaded. Cannot process request.")
            return jsonify({
                'error': 'Service temporarily unavailable. Please try again later.',
                'details': 'Required model artifacts failed to load'
            }), 503
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize artifacts
def verify_artifacts():
    """Verify that all required artifacts are properly loaded"""
    try:
        locations = util.get_location_names()
        if not locations:
            logger.error("Locations list is empty")
            return False
        
        # Try a test prediction
        test_price = util.get_estimated_price(locations[0], 1000, 2, 2)
        if not isinstance(test_price, (int, float)):
            logger.error(f"Test prediction failed: {test_price}")
            return False
            
        logger.info("Artifacts verification successful")
        return True
    except Exception as e:
        logger.error(f"Artifacts verification failed: {str(e)}")
        return False

def initialize_artifacts(max_retries=3):
    """Initialize artifacts with retry mechanism"""
    global artifacts_loaded
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Loading artifacts (attempt {attempt + 1}/{max_retries})...")
            
            if util.load_saved_artifacts():
                if verify_artifacts():
                    artifacts_loaded = True
                    logger.info("Artifacts loaded and verified successfully")
                    return True
                else:
                    logger.error("Artifacts loaded but verification failed")
            else:
                logger.error("Failed to load artifacts")
                
        except Exception as e:
            logger.error(f"Error during artifact loading: {str(e)}")
            logger.debug(f"Stacktrace: {traceback.format_exc()}")
        
        if attempt < max_retries - 1:
            logger.info(f"Retrying in 2 seconds...")
            time.sleep(2)
    
    logger.critical("Failed to load artifacts after all attempts")
    return False

# Initialize artifacts before starting the server
artifacts_loaded = initialize_artifacts()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint to check service health"""
    global artifacts_loaded
    status = {
        'status': 'healthy' if artifacts_loaded else 'degraded',
        'artifacts_loaded': artifacts_loaded,
        'timestamp': time.time()
    }
    return jsonify(status), 200 if artifacts_loaded else 503

@app.route('/api/get_location_names', methods=['GET'])
def get_location_names():
    try:
        response = jsonify({
            'locations': util.get_location_names(),
            'status': 'success'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        print("Locations sent successfully:", util.get_location_names())  # Debug log
        return response
    except Exception as e:
        print("Error in get_location_names:", str(e))  # Error log
        return jsonify({
            'locations': [],
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/predict_home_price', methods=['GET','POST'])
def predict_home_price():
    global artifacts_loaded
    logger.debug("Received prediction request")
    
    if not artifacts_loaded:
        logger.warning("Attempting to reload artifacts...")
        artifacts_loaded = initialize_artifacts()
        if not artifacts_loaded:
            return jsonify({
                'error': 'Service temporarily unavailable',
                'details': 'System initialization incomplete'
            }), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid input',
                'details': 'Request body is empty'
            }), 400

        # Validate required fields
        required_fields = ['total_sqft', 'bhk', 'bath', 'location']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'details': f'Missing: {", ".join(missing_fields)}'
            }), 400

        # Parse and validate input values
        try:
            total_sqft = float(data['total_sqft'])
            bhk = int(data['bhk'])
            bath = int(data['bath'])
            location = str(data['location'])
        except ValueError as ve:
            return jsonify({
                'error': 'Invalid input format',
                'details': str(ve)
            }), 400

        # Validate value ranges
        if total_sqft <= 0 or bhk <= 0 or bath <= 0:
            return jsonify({
                'error': 'Invalid input values',
                'details': 'All numeric values must be positive'
            }), 400

        # Get prediction
        result = util.get_estimated_price(location, total_sqft, bhk, bath)
        
        if isinstance(result, str):  # Error message
            logger.warning(f"Prediction failed: {result}")
            return jsonify({
                'error': 'Prediction failed',
                'details': result
            }), 400
            
        logger.info(f"Successful prediction: {result}")
        return jsonify({'estimated_price': result})

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        logger.debug(f"Stacktrace: {traceback.format_exc()}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle any uncaught exceptions"""
    logger.error(f"Uncaught exception: {str(e)}")
    logger.debug(f"Stacktrace: {traceback.format_exc()}")
    return jsonify({
        'error': 'Internal server error',
        'details': str(e)
    }), 500

if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    print("Loading artifacts...")
    util.load_saved_artifacts()
    print("\nStarting server at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
