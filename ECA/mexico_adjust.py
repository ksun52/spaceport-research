import pdb
import rasterio
from rasterio.mask import mask, raster_geometry_mask
from shapely.geometry import Polygon
import os
import matplotlib.pyplot as plt
import numpy as np
import json
import fiona
from pop_flown_over import get_corners

# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)

# Mexico boundary mask 
with fiona.open(os.path.join(file_directory, "mexico/mexican-states.shp"), 'r') as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]
masked1, _, _ = raster_geometry_mask(dataset, shapes, all_touched=True, invert=True, crop=False)


# Load data from the JSON file
with open("ECA/county_data.json", "r") as file:
    data = json.load(file)

# Loop through every county to get and plot the launch angles 
for county in data:
    if not county["number_list"]:
        continue
    
    start_point = (county["center_lon"], county["center_lat"])
    print(f"checking {county['NAME']} at {start_point}")
    for angle in county["number_list"]: # angle is in launch angle convention 
        angle2 = (90 - angle) % 360 # polar angle convention 
        vertices = get_corners(start_point, angle2, spread=10, dataset=dataset)
        if not vertices:
            print("no")
            pdb.set_trace()

        # Create a Polygon geometry for the flyover zone
        flyover_polygon = Polygon(vertices)

        # US map area flown over mask 
        masked2, _, _ = raster_geometry_mask(dataset, [flyover_polygon], all_touched=True, invert=True, crop=False)

        if np.sum(np.multiply(masked1, masked2)) > 0:
            print(f"{angle} is not ok - intersects Mexico")
        else:
            print(f"{angle} ok")


# Close the dataset
dataset.close()