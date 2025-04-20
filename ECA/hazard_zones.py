"""
Loop through JSON to add info on polygon coordinates 
"""
import json
import os 
import rasterio 
from shapely import Polygon, wkt
from pop_flown_over import get_corners



# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)

# THIS IS THE VALUE TO CHANGE FOR HAZARD ZONE SPREADS 
spread = 10

# Load data from the JSON file
# SPREAD IS HERE
with open(f"ECA/minusCountyPop_pop50_spread{spread}.json", "r") as file:
    data = json.load(file)

# Loop through every county to add a list of polygons 

for county in data:
    hazard_zones = []
    county_lon = float(county["center_lon"])
    county_lat = float(county["center_lat"])
    county_coord = (county_lon, county_lat)

    for angle in county["number_list"]:
        # convert to polar coordinate convention - 0 degrees along positive x axis and increase counterclockwise
        angle2 = (90 - angle) % 360

        # SPREAD IS HERE
        vertices = get_corners(county_coord, angle2, spread=spread, dataset=dataset)
        
        if vertices == None:
            continue
        else:
            hazard_area = Polygon(vertices)
            hazard_string = wkt.dumps(hazard_area)
            hazard_zones.append(hazard_string)
    
    county["hazard_zones"] = hazard_zones


# Save the modified data back to the file
# SPREAD IS HERE
with open(f"ECA/minusCountyPop_pop50_spread{spread}_hazards.json", "w") as file:
    json.dump(data, file, indent=4)  # indent for pretty formatting
