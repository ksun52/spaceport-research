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

import geopandas as gpd


# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)
plt.imshow(dataset.read(1), cmap='gray')


# Load data from the JSON file
# filename = "ECA/county_data_pop5000_spread10.json"
# filename = "ECA/county_data_pop5000_spread15.json"
filename = "ECA/county_data_pop5000_spread10_hazards.json"
with open(filename, "r") as file:
    data = json.load(file)

# Loop through every county to get and plot the launch angles 
magnitude = 3
color = 'lime'
acceptable_counties = ["Del Norte", "Presidio", "Wahkiakum", "Dare", "Gulf", "Zapata"]


for county in data:
    # if not county["number_list"] or county["NAME"] != "Hidalgo":
    #     continue
    if not county["number_list"]:
        continue

    # use our list of acceptable counties 
    if county["NAME"] not in acceptable_counties:
        continue
    
    start_point = (county["center_lon"], county["center_lat"])
    sp_plot_coords = dataset.index(start_point[0], start_point[1])
    plt.plot(sp_plot_coords[1], sp_plot_coords[0], markeredgecolor='red', markerfacecolor='red',  marker="*", markersize=10)
    angle_set = []  # plot all sets of angle ranges 

    # pdb.set_trace()

    for angle in county["number_list"]: # angle is in launch angle convention 
        if not angle_set or angle_set[-1] == angle - 1:
            angle_set.append(angle)
        
        else:
            angle_vertices = [start_point]

            # get point for the first angle 
            polar_angle = (90 - angle_set[0]) % 360
            end_lon = start_point[0] + magnitude * np.cos(math.radians(polar_angle))
            end_lat = start_point[1] + magnitude * np.sin(math.radians(polar_angle))
            angle_vertices.append((end_lon, end_lat))

            # get point for the second angle 
            polar_angle = (90 - angle_set[-1]) % 360
            end_lon = start_point[0] + magnitude * np.cos(math.radians(polar_angle))
            end_lat = start_point[1] + magnitude * np.sin(math.radians(polar_angle))
            angle_vertices.append((end_lon, end_lat))
            
            # transform (long, lat) into pixel coordinates (how far down, how far right) where (0,0) is top left
            pixel_coords = [dataset.index(vertex[0], vertex[1]) for vertex in angle_vertices]
            # transform  pixel_coords into the convention for plt.plot which is (how far right, how far down)
            pixel_plot_coords = [(i[1], i[0]) for i in pixel_coords]
            angle_vertices_plot = Polygon(pixel_plot_coords)

            plt.plot(*angle_vertices_plot.exterior.xy, color=color, linewidth=2)
            plt.fill(*angle_vertices_plot.exterior.xy, color=color)
            angle_set.clear()
            
        

    # plot one more 
    if angle_set:
        angle_vertices = [start_point]

        # get point for the first angle 
        polar_angle = (90 - angle_set[0]) % 360
        end_lon = start_point[0] + magnitude * np.cos(math.radians(polar_angle))
        end_lat = start_point[1] + magnitude * np.sin(math.radians(polar_angle))
        angle_vertices.append((end_lon, end_lat))

        # get point for the second angle 
        polar_angle = (90 - angle_set[-1]) % 360
        end_lon = start_point[0] + magnitude * np.cos(math.radians(polar_angle))
        end_lat = start_point[1] + magnitude * np.sin(math.radians(polar_angle))
        angle_vertices.append((end_lon, end_lat))

        angle_vertices.append(start_point)
        
        # transform (long, lat) into pixel coordinates (how far down, how far right) where (0,0) is top left
        pixel_coords = [dataset.index(vertex[0], vertex[1]) for vertex in angle_vertices]
        # transform  pixel_coords into the convention for plt.plot which is (how far right, how far down)
        pixel_plot_coords = [(i[1], i[0]) for i in pixel_coords]
        angle_vertices_plot = Polygon(pixel_plot_coords)

        # plt.imshow(dataset.read(1), cmap='gray')
        plt.plot(*angle_vertices_plot.exterior.xy, color=color, linewidth=2)
        plt.fill(*angle_vertices_plot.exterior.xy, color=color)
        angle_set.clear()
            
    
    
plt.show()
print("end")