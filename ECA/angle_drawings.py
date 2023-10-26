import os
import json
import numpy as np
import math
import pdb
from enum import IntEnum

import rasterio
from rasterio.mask import mask

from shapely.geometry import Polygon
import matplotlib.pyplot as plt


# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)
plt.imshow(dataset.read(1), cmap='gray')

#pdb.set_trace()

# Load data from the JSON file
# filename = "ECA/county_data_pop5000_spread10.json"
# filename = "ECA/county_data_pop5000_spread15.json"
filename = "ECA/county_data_pop5000_spread10_hazards.json"
with open(filename, "r") as file:
    data = json.load(file)

# Loop through every county to get and plot the launch angles 
magnitude = 2
for county in data:
    # if not county["number_list"] or county["NAME"] != "Hidalgo":
    #     continue
    if not county["number_list"]:
        continue
    
    start_point = (county["center_lon"], county["center_lat"])
    for angle in county["number_list"]: # angle is in launch angle convention 
        polar_angle = (90 - angle) % 360
        end_lon = start_point[0] + magnitude * np.cos(math.radians(polar_angle))
        end_lat = start_point[1] + magnitude * np.sin(math.radians(polar_angle))
        new_point = (end_lon, end_lat)

        line = [start_point, new_point]
        
        # transform (long, lat) into pixel coordinates (how far down, how far right) where (0,0) is top left
        pixel_coords = [dataset.index(vertex[0], vertex[1]) for vertex in line]
        # transform  pixel_coords into the convention for plt.plot which is (how far right, how far down)
        pixel_plot_coords = [(i[1], i[0]) for i in pixel_coords]
        #launch_trajectory_pixels = Polygon(pixel_plot_coords)
        #plt.plot(*launch_trajectory_pixels.exterior.xy, color='red', linewidth=2)
        #pdb.set_trace()
        x1 = [pixel_plot_coords[0][0], pixel_plot_coords[1][0]]
        y1 = [pixel_plot_coords[0][1], pixel_plot_coords[1][1]]
        plt.plot(x1, y1, color='b')
        
        
    
    
plt.show()
print("end")