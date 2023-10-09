'''
This code contains helper functions to figure out what launch angles are feasible 
'''

import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
import pdb 
from scipy.stats import laplace

from geopy.geocoders import Nominatim
from shapely.geometry import LineString
import shapefile
import geopy.distance
from geopy.distance import geodesic
from geopy import Point


# just for playing around 
def get_county_name(latitude, longitude):
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    address = location.raw['address']
    county = address.get('county')
    if county:
        return county
    else:
        print("county not found")
        return None

# just for playing around 
def get_counties_along_line(start_lat, start_lon, end_lat, end_lon):
    geolocator = Nominatim(user_agent="my-app")
    line = LineString([(start_lon, start_lat), (end_lon, end_lat)])
    
    dist = geopy.distance.geodesic((start_lat, start_lon), (end_lat, end_lon)).km

    segment_count = int(dist // 10)   # Number of segments to break the line into
    segments = []
    for i in range(segment_count):
        fraction = float(i) / segment_count
        point = line.interpolate(fraction, normalized=True)
        lat, lon = point.y, point.x
        location = geolocator.reverse(f"{lat}, {lon}")
        address = location.raw['address']
        county = address.get('county')
        if county and county not in segments:
            segments.append(county)

    return segments

# checks counties between start to end
# returns true if everything along the line is ok to fly over
# returns false if there is a county, Canada, or Mexico underneath trajectory 
def check_counties_along_line(start_lat, start_lon, end_lat, end_lon, dist, start_county):
    geolocator = Nominatim(user_agent="my-app")

    line = LineString([(start_lon, start_lat), (end_lon, end_lat)])
    segment_count = int(dist // 10)   # Number of segments to break the line into
    
    for i in range(segment_count):
        fraction = float(i) / segment_count
        point = line.interpolate(fraction, normalized=True)
        lat, lon = point.y, point.x
        location = geolocator.reverse(f"{lat}, {lon}")
        if isRestricted(location, start_county):
            return False
        
    return True
        

# returns true if this location cannot be flown over if it is Canada, Mexico, or a US county 
# the start county can be flown over 
def isRestricted(location, start_county):
    if location == None:
        return False
    
    address = location.raw['address']
    nation = address.get('country')
    county = address.get('county')

    if nation == 'Canada' or nation == 'México':
        return True
    elif nation == 'United States' and county == None:
        return False 
    elif county == start_county:
        return False
    else:
        return True 



def end_coords(start_lat, start_lon, dist, angle):
    # https://stackoverflow.com/questions/4530943/calculating-a-gps-coordinate-given-a-point-bearing-and-distance/4531227#4531227
    end_coords = geodesic(kilometers=dist).destination(Point(start_lat, start_lon), angle)
    end_lat = end_coords.latitude
    end_lon = end_coords.longitude
    return end_lat, end_lon


'''
USED FOR TESTING PURPOSES 
'''
def main():
    # Example usage for getting single county name 
    latitude = 40.65751341 #42.28475955964087 #47.42615411566691 #37.7749
    longitude = -73.83880302 #-83.85930193562201 #-122.29543154002945 #-122.4194
    county = get_county_name(latitude, longitude)
    print(county)

    # Example usage for getting multiple counties 
    '''start_lat = 37.7749
    start_lon = -122.4194
    end_lat = 34.0522
    end_lon = -118.2437

    counties = get_counties_along_line(start_lat, start_lon, end_lat, end_lon)
    print(counties)'''
    
if __name__ == "__main__":
    main()
    