# get a plot of the US border based on CSV file for the latitude and longitude 

import numpy as np
import matplotlib.pyplot as plt
import cv2


import pdb

if __name__ == "__main__":
   
    # get lat lon coordinates
    # us_continental takes us_all.csv but deletes hawaii, and territories
    lat_long = np.genfromtxt("us_continental.csv", delimiter=',')
    latitude = lat_long[:, 0]
    longitude = lat_long[:, 1]
    
    # plot
    plt.scatter(longitude, latitude, s=0.5)
    plt.title("US Border")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    
    plt.show()
    plt.close()

