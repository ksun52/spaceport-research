"""
Works - takes 8 hours to run one test for 15 degree spread 
Use find_trajectories2 for faster implementation using pre-calculations of angle segments then adding and subtracting as you go 
"""

import os
import json
import numpy as np
import csv 

import rasterio
from rasterio.mask import mask, raster_geometry_mask
from shapely.geometry import Point
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import fiona
import pdb

from pop_flown_over import get_corners


# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)

# Open up the Mexico shapefile to check mexico boundary 
# get Mexico mask 
with fiona.open(os.path.join(file_directory, "mexico/mexican-states.shp"), 'r') as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]
mex_mask, _, _ = raster_geometry_mask(dataset, shapes, all_touched=True, invert=True, crop=False)

#pdb.set_trace()
counties_data = []

# create polygon for interior united states that you dont want to waste time checking 
# dataset.index(lon, lat) --> row, col (down, over)
# dataset.xy(row, col) --> lon, lat 
interior = Polygon([dataset.xy(1600, 700), dataset.xy(0, 700), dataset.xy(0, 6000), dataset.xy(2000, 4800), dataset.xy(1600, 700)])


# open the list of counties
with open(os.path.join(file_directory, 'graphic.csv')) as county_file:
    csv_reader = csv.reader(county_file)

    # skip header rows 
    for i in range(1):
        next(csv_reader)

    for row in csv_reader:
        county_name = row[5]
        county_LSAD = row[6]
        county_lon = float(row[10])
        county_lat = float(row[11])

        county_coord = (county_lon, county_lat)
        possible_angles = []

        # move on if the county is in this region of the US
        if interior.contains(Point(county_lon, county_lat)):
            pass
        
        elif row[16] and float(row[16]) < 5000: # set limit for population density for faster runtime 

            # launch azimuth angles: 0 degrees is north and increases clockwise 
            for angle in range(0, 360):

                # convert to polar coordinate convention - 0 degrees along positive x axis and increase counterclockwise
                angle2 = (90 - angle) % 360
                
                # can edit spread - for now using 10 degrees 
                vertices = get_corners(county_coord, angle2, spread=15, dataset=dataset)
                if vertices == None:
                    continue
                else:
                    flyover_polygon = Polygon(vertices)

                    # do a secondary mexico flyover check with the created polygon 
                    flyover_mask, _, _ = raster_geometry_mask(dataset, [flyover_polygon], all_touched=True, invert=True, crop=False)
                    if np.sum(np.multiply(mex_mask, flyover_mask)) > 0:
                        continue
                    else:    
                        # population flown over 
                        masked_image, masked_transform = mask(dataset, [flyover_polygon], all_touched=True, nodata=0, crop=False)
                        pop = np.sum(masked_image)

                        # for now, set population limit to 5000 people being flown over 
                        #breakpoint()
                        if pop < 5000:
                            possible_angles.append(angle)
            
        data = {
            "NAME": county_name,
            "LSAD": county_LSAD,
            "center_lat": county_lat,
            "center_lon": county_lon,
            "number_list": possible_angles
        }
        breakpoint()
        counties_data.append(data)
        print(f"finished checking {county_name} county")
    
# Write the data to a JSON file
json_filename = "county_data_pop5000_spread15.json"
with open(os.path.join(file_directory, json_filename), "w") as json_file:
    json.dump(counties_data, json_file, indent=4)
    print("all done!")
