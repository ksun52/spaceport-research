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
from shapely.wkt import loads 

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

# codes for states on interior of US 
state_set = {'02', '04', '05', '08', '15', '16', '17', '18', '19', '20', '21', '26', '27', '29', '30', '31', '32', '35', '38', '39', '40', '42', '46', '47', '49', '50', '54', '55', '56'}

# open the list of counties
with open(os.path.join(file_directory, 'graphic.csv')) as county_file:
    csv_reader = csv.reader(county_file)

    # skip header rows 
    for _ in range(1):
    # for _ in range(2930):
        next(csv_reader)

    for row in csv_reader:
        county_name = row[5]
        county_LSAD = row[6]
        county_lon = float(row[10])
        county_lat = float(row[11])
        
        county_state = row[3]
        # pdb.set_trace()

        county_coord = (county_lon, county_lat)
        possible_angles = []

        # check if county is in one of the interior states
        if county_state in state_set:
            print(f"skipping {county_name} county")
            
        # move on if the county is in this region of the US
        elif interior.contains(Point(county_lon, county_lat)):
            print(f"skipping {county_name} county")
        
        elif row[16] and float(row[16]) < 5000: # set limit for population density for faster runtime 
            # print(f"checking possible angles for  {county_name} county")

            county_poly = loads(row[8])

            # launch azimuth angles: 0 degrees is north and increases clockwise 
            for angle in range(0, 360):
                # pdb.set_trace()
                # if county is on left half of US, dont launch to the east 
                if county_lon < -98.5208333355421:
                    if angle >= 0 and angle <= 145:
                        # print(f"{county_name} on left half - dont launch east")
                        continue
                
                # if longitude is far enough west but not too far west, dont launch upwards
                if -114 < county_lon and county_lon < -81.85416666887528:
                    if angle <= 90 or angle >= 270:
                        # print(f"{county_name} on left half - dont launch north")
                        continue
                
                # if county is on the east side but not southeast, dont launch west 
                if -114 < county_lon and county_lat > 31:
                    if angle >= 190 or angle <= 20:
                        # print(f"{county_name} on right half - dont launch west")
                        continue
                


                # convert to polar coordinate convention - 0 degrees along positive x axis and increase counterclockwise
                angle2 = (90 - angle) % 360
                
                # can edit spread - for now using 10 degrees 
                vertices = get_corners(county_coord, angle2, spread=15, dataset=dataset)
                if vertices == None:
                    # pdb.set_trace()
                    continue
                else:
                    flyover_polygon = Polygon(vertices)
                    
                    # do a secondary mexico flyover check with the created polygon 
                    flyover_mask, _, _ = raster_geometry_mask(dataset, [flyover_polygon], all_touched=True, invert=True, crop=False)
                    if np.sum(np.multiply(mex_mask, flyover_mask)) > 0:
                        continue
                    else:    
                        # population flown over - OLD METHOD: just check flyover region
                        # masked_image, masked_transform = mask(dataset, [flyover_polygon], all_touched=True, nodata=0, crop=False)
                        # pop = np.sum(masked_image)
                        
                        # population flown over - NEW METHOD: take away the pop from county itself 
                        masked_image1, _ = mask(dataset, [flyover_polygon, county_poly], all_touched=True, nodata=0, crop=False)
                        masked_image2, _ = mask(dataset, [county_poly], all_touched=True, nodata=0, crop=False)
                        pop = np.sum(masked_image1) - np.sum(masked_image2)

                        # for now, set population limit to 5000 people being flown over 
                        #breakpoint()
                        if pop < 1000:
                            possible_angles.append(angle)
            
        data = {
            "NAME": county_name,
            "LSAD": county_LSAD,
            "center_lat": county_lat,
            "center_lon": county_lon,
            "number_list": possible_angles
        }
        # breakpoint()
        counties_data.append(data)
        print(f"finished checking {county_name} county")
    
# Write the data to a JSON file
json_filename = "faster_county_data_pop5000_spread15.json"
with open(os.path.join(file_directory, json_filename), "w") as json_file:
    json.dump(counties_data, json_file, indent=4)
    print("all done!")

