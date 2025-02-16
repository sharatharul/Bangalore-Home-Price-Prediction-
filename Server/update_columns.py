import json

# Path to your columns.json file
json_file_path = "./artifacts/columns.json"

# Load the JSON file
with open(json_file_path, "r") as f:
    data = json.load(f)

# Print initial number of features
print("Initial number of features:", len(data["data_columns"]))

# Remove invalid entries
invalid_entries = ["{'rewrites': [{'source': '/(.*)', 'destination': '/'}]}"]
data["data_columns"] = [feature for feature in data["data_columns"] if feature not in invalid_entries]

# Ensure the number of features is 243
while len(data["data_columns"]) > 243:
    # Remove extra features (manually identify which to remove)
    data["data_columns"].pop()

# Print updated number of features
print("Updated number of features:", len(data["data_columns"]))

# Save the updated columns.json
with open(json_file_path, "w") as f:
    json.dump(data, f, indent=4)

print("Updated columns.json file saved successfully.")
