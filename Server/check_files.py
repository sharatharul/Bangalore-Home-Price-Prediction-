import json
import pickle
import numpy as np

__locations = None
__data_columns = None
__model = None

def get_estimated_price(location, sqft, bhk, bath):
    if __data_columns is None or __model is None:
        return "Model or data columns not loaded"
    try:
        loc_index = __data_columns.index(location.lower())
    except ValueError:
        loc_index = -1

    # Print the number of data columns
    print(f"Number of data columns: {len(__data_columns)}")
    print(f"Data columns: {__data_columns}")

    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index >= 0:
        x[loc_index] = 1

    n_features = x.shape[0]
    if n_features != __model.n_features_in_:
        raise ValueError(
            f"X has {n_features} features, but {__model.__class__.__name__} "
            f"is expecting {__model.n_features_in_} features as input."
        )

    print(f"Feature array (x) before prediction: {x}")

    return round(__model.predict([x])[0], 2)

def load_saved_artifacts():
    print("loading saved artifacts...start")
    global __data_columns
    global __model
    global __locations

    try:
        with open("./artifacts/columns.json", "r") as f:
            data = json.load(f)
            if "data_columns" not in data:
                raise ValueError("Invalid format in columns.json")
            __data_columns = data["data_columns"]
            __locations = __data_columns[3:]  # First 3 columns are sqft, bath, bhk

        print(f"Number of features in columns.json: {len(__data_columns)}")

        with open('./artifacts/banglore_home_prices_model.pickle', 'rb') as f:
            __model = pickle.load(f)

        print("loading saved artifacts...done")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError:
        print("Error: columns.json is not a valid JSON file")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def get_location_names():
    return __locations if __locations else []

def get_data_columns():
    global __data_columns
    return __data_columns if __data_columns else []

if __name__ == '__main__':
    load_saved_artifacts()
    print(get_location_names())
    print(get_estimated_price('1st Phase JP Nagar', 1000, 3, 3))
    print(get_estimated_price('1st Phase JP Nagar', 1000, 2, 2))
    print(get_estimated_price('Kalhalli', 1000, 2, 2))  # other location
    print(get_estimated_price('Ejipura', 1000, 2, 2))  # other location
