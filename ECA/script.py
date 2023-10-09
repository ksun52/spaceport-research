import json

# Load data from the JSON file
with open("ECA/county_data_BACKUP.json", "r") as file:
    data = json.load(file)

# Loop through every county to get rid of outside quotations
for county in data:
    county["county_name"] = county["county_name"][1:-1]

# Save the modified data back to the file
with open("ECA/county_data_BACKUP.json", "w") as file:
    json.dump(data, file, indent=4)  # indent for pretty formatting
