from joblib import load
from sklearn.linear_model import LinearRegression
import numpy as np
import json
import pickle
import warnings
import logging
import os

warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

__locations = None
__data_columns = None
__model = None


def predict(input_data):
    if __model is None:
        raise ValueError("Model is not loaded")
    return

def get_estimated_price(location, total_sqft, bhk, bath):
    print("\n=== Debug Information ===")
    print(f"Input parameters:")
    print(f"Location: {location}")
    print(f"Total Sqft: {total_sqft}")
    print(f"BHK: {bhk}")
    print(f"Bath: {bath}")

    # First check if model and data are loaded
    if __data_columns is None or __model is None:
        print("Error: Model or data columns not loaded")
        print(f"__data_columns is None: {__data_columns is None}")
        print(f"__model is None: {__model is None}")
        return "Model or data columns not loaded"

    try:
        # Create feature vector
        x = np.zeros(len(__data_columns))
        x[0] = total_sqft
        x[1] = bath
        x[2] = bhk

        # Handle location encoding
        try:
            loc_index = __data_columns.index(location.lower())
            x[loc_index] = 1
            print(f"Location '{location}' encoded at index: {loc_index}")
        except ValueError:
            print(f"Warning: Location '{location}' not found in model data")
            # Continue with prediction even if location is not found
            pass

        print("\nFeature vector created:")
        print(f"Length: {len(x)}")
        print(f"First few values: {x[:5]}")

        # Make prediction
        prediction = __model.predict([x])[0]
        final_price = round(prediction, 2)
        print(f"Successfully predicted price: {final_price}")
        return final_price

    except Exception as e:
        print(f"Error during prediction process: {str(e)}")
        print(f"Error type: {type(e)}")
        return f"Error during prediction: {str(e)}"


def load_saved_artifacts():
    print("\n=== Loading Artifacts ===")
    global __data_columns
    global __model
    global __locations

    try:
        # Try both relative and absolute paths
        artifacts_paths = [
            "./artifacts",  # relative to current directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts"),  # relative to script
            "../artifacts",  # one directory up
            "artifacts"  # direct folder name
        ]

        artifacts_dir = None
        for path in artifacts_paths:
            if os.path.exists(path):
                artifacts_dir = path
                break

        print("\nPath Search Results:")
        for path in artifacts_paths:
            print(f"Checking path: {os.path.abspath(path)} - {'Found' if os.path.exists(path) else 'Not Found'}")

        if not artifacts_dir:
            print("\nERROR: Could not find artifacts directory in any of the searched locations")
            print(f"Current working directory: {os.getcwd()}")
            return False

        print(f"\nUsing artifacts directory: {os.path.abspath(artifacts_dir)}")
        
        # Load columns with enhanced error checking
        columns_path = os.path.join(artifacts_dir, "columns.json")
        if not os.path.exists(columns_path):
            print(f"ERROR: {columns_path} not found")
            return False

        print("\n1. Loading columns.json...")
        try:
            with open(columns_path, "r") as f:
                data = json.load(f)
                if "data_columns" not in data:
                    print("ERROR: Invalid format in columns.json - 'data_columns' key not found")
                    return False
                __data_columns = data["data_columns"]
                __locations = __data_columns[3:]  # first 3 columns are sqft, bath, bhk
                print(f"✓ Columns loaded successfully. Total columns: {len(__data_columns)}")
                print(f"✓ Total locations loaded: {len(__locations)}")
                print(f"✓ First few locations: {__locations[:5]}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON format in columns.json: {str(e)}")
            return False

        # Load model
        model_path = os.path.join(artifacts_dir, 'banglore_home_prices_model.pickle')
        if not os.path.exists(model_path):
            print(f"Error: {model_path} not found")
            return False

        print("\n2. Loading model file...")
        with open(model_path, 'rb') as f:
            __model = pickle.load(f)
            print(f"Model loaded successfully. Type: {type(__model)}")

        # Verify loaded artifacts
        if __model is None or __data_columns is None or __locations is None:
            print("Error: One or more artifacts failed to load properly")
            return False

        print("\nAll artifacts loaded successfully")
        return True

    except Exception as e:
        print(f"Error loading artifacts: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
        return False


def get_location_names():
    global __locations
    if __locations is None:
        print("Warning: Locations not loaded")
        return []
    return __locations


def get_data_columns():
    global __data_columns
    return __data_columns if __data_columns else []


if __name__ == '__main__':
    print("=== Starting Test Cases ===")
    if not load_saved_artifacts():
        print("Failed to load artifacts. Exiting tests.")
        exit(1)

    # Define test cases
    test_cases = [
        ('1st Phase JP Nagar', 1000, 3, 3),
        ('1st Phase JP Nagar', 1000, 2, 2),
        ('Kalhalli', 1000, 2, 2),
        ('Ejipura', 1000, 2, 2)
    ]

    # Run all test cases
    print("\n=== Running Test Cases ===")
    for i, (location, sqft, bhk, bath) in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        print(f"Testing: {location}, {sqft} sqft, {bhk} BHK, {bath} bath")
        result = get_estimated_price(location, sqft, bhk, bath)
        print(f"Result for Test Case {i}: {result}")
        print("=" * 50)
