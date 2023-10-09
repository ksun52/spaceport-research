'''
This code gets lat long transformations from NOAA 
Dont use this - it is too slow to convert xyz to lat long 
'''

import requests
import json
import pdb
import numpy as np
import csv 

def main():
    URL = "https://geodesy.noaa.gov/api/ncat/xyz?inDatum=nad83(2011)&outDatum=nad83(NSRS2007)&x=-217687.279&y=-5069012.406&z=3852223.048"
    r = requests.get(url = URL)
    
    if (r.status_code != 200):
        print("error: status code" + r.status_code)
        return

    data = r.json()
    print(data)

'''
#Just throwing this here for reference -- this makes the code run WAAAY too slow 
# returns lat, lon, height
def get_lat_lon(x, y, z):
    URL = "https://geodesy.noaa.gov/api/ncat/xyz?inDatum=nad83(2011)&outDatum=nad83(NSRS2007)&x=%d&y=%d&z=%d" % (x,y,z)
    r = requests.get(url = URL)
    
    if (r.status_code != 200):
        print("lat lon conversion error: status code" + r.status_code)
        return

    data = r.json()
    #pdb.set_trace()
    return data['destLat'], data['destLon'], data['destEht']
'''


if __name__ == "__main__":
    main()
    
    