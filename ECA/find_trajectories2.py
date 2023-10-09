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

from pop_flown_over import get_corners, all_angle_slices


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
    for i in range(39):
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
            #pdb.set_trace()
            pass
        
        elif row[16] and float(row[16]) < 5000: # set limit for population density for faster runtime 
            spread = 15
            # returns slices in polar convention - dictionary of left_angle 1 degree slice --> population (or None)
            angle_info = all_angle_slices(county_coord, spread=spread, dataset=dataset, mexico_mask=mex_mask)

            # launch azimuth angles: 0 degrees is north and increases clockwise 
            for angle in range(0, 360):

                pop_sum = 0
                invalid_slice_seen = False

                for i in range(spread):
                    slice = (angle - spread/2 + i) % 360

                    # convert to polar coordinate convention - 0 degrees along positive x axis and increase counterclockwise
                    slice2 = (90 - slice) % 360
                    add_pop = angle_info[slice2]

                    if add_pop != None:
                        pop_sum += angle_info[slice2]
                    else:
                        invalid_slice_seen = True
                        break

                # for now, set population limit to 5000 people being flown over 
                if not invalid_slice_seen and pop_sum < 5000:
                    possible_angles.append(angle)
            
        data = {
            "NAME": county_name,
            "LSAD": county_LSAD,
            "center_lat": county_lat,
            "center_lon": county_lon,
            "number_list": possible_angles
        }
        pdb.set_trace()
        counties_data.append(data)
        print(f"finished checking {county_name} county")
    
# Write the data to a JSON file
json_filename = "county_data_pop5000_spread15.json"
with open(os.path.join(file_directory, json_filename), "w") as json_file:
    json.dump(counties_data, json_file, indent=4)
    print("all done!")

