# from flightclub.io, latitude/longitude data is pulled from rocket launch trajectory plots
# data is pulled using webplotdigitizer https://automeris.io/WebPlotDigitizer/
# generate list of latitude and list of longitude then plot


import numpy as np
import matplotlib.pyplot as plt
import cv2

import pdb


def split_data(dataset):
    # data comes in as a numpy array with N lattitudes and N logitudes in the form
    # time latitude time longitude
    # the 2 times should be equal 
    # return in the form of latitude (Nx1) and longitude (Nx1)
    lat_long = np.genfromtxt(dataset + "/" + dataset + ".csv", delimiter=',')
    return (lat_long[:, 1], lat_long[:, 3])


def quick_plot(dataset):
    lat_long = np.genfromtxt(dataset + "/" + dataset + ".csv", delimiter=',')
    plt.plot(lat_long[:, 0], lat_long[:, 1])
    plt.plot(lat_long[:, 2], lat_long[:, 3])
    plt.show()


# flights: 
# crew6 = Falcon 9 + Crew Dragon (Kennedy)
# SL5-2 = Starlink Group 5-2 = Falcon 9 Block 5 (Cape Canaveral)
# electron = Rocketlab Electron (Virginia LC2 Wallops Island)
# USSF67 = Falcon Heavy (Kennedy)
# artems = Artemis 1 = SLS Block 1 Crew (Kennedy)
# JPSS = JPSS 2 = Atlas V 401 (Vandenberg AFB)

if __name__ == "__main__":
   
    # i messed up and electron needs to be redone :(
    dataset = "crew6"

    latitude, longitude = split_data(dataset)
    
    #pdb.set_trace()

    plt.plot(longitude, latitude)
    plt.title("Flight Trajectory of " + dataset)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.savefig(fname = dataset + "/" + dataset + "img.png", format = "png")
    plt.show()
    plt.close()

    #quick_plot(dataset)


