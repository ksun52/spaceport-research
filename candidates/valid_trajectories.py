'''
- This code returns valid launch angles for the given coastal cities 
- launch angles are checked for every degree 
- along the trajectory, if there are any US counties on the path, the trajectory is invalid 
'''

import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
import pdb 
from scipy.stats import laplace
import csv

from geopy.geocoders import Nominatim
from shapely.geometry import LineString
import shapefile
from geopy.distance import geodesic
from geopy import Point

from common import *


def get_valid_trajectories():
    filename = "coastal_counties.csv"

    with open(filename, 'r') as infile:
        csv_reader = csv.reader(infile)

        with open('ranges.csv', 'a') as outfile:
            writer = csv.writer(outfile)
            
            # skip rows 
            for i in range(141):
                next(csv_reader)

            for row in csv_reader:  # skip the first row 
                print(f'checking {row[0]}')
                angle_list = county_valid_trajectories(float(row[4]), float(row[5]))
                writer.writerow([row[0], angle_list])
            


def county_valid_trajectories(start_lat, start_lon):
    distance = 400    # in kilometers - distance before rocket is above unregulated airspace 
    start_county = get_county_name(start_lat, start_lon)

    if start_county == None:
        return []

    angle_list = []
    sector_start = None
    sector_end = None
    
    for angle in range(360):
        print(f'checking angle: {angle}')
        end_lat, end_lon = end_coords(start_lat, start_lon, distance, angle)
        valid_angle = check_counties_along_line(start_lat, start_lon, end_lat, end_lon, distance, start_county)
        
        if valid_angle:
            if not sector_start:
                sector_start = angle
            
            sector_end = angle
        else:
            if sector_start:
                angle_list.append([sector_start, sector_end])
            
            sector_start = None
            sector_end = None

    if sector_start:
        angle_list.append([sector_start, sector_end])

    return angle_list
    




def main():
    '''lat = 30.66096966
    lon = -87.74984008 
    dist = 1    # km
    angle = 0
    print(geodesic(kilometers=dist).destination(Point(lat, lon), angle).format_decimal())
    print(geodesic(kilometers=dist).destination(Point(lat, lon), angle))
    print(geodesic(kilometers=dist).destination(Point(lat, lon), angle).latitude)
    print(geodesic(kilometers=dist).destination(Point(lat, lon), angle).longitude)'''
    get_valid_trajectories()

if __name__ == "__main__":
    main()