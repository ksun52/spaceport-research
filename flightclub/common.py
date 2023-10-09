'''
This code has helper functions for processing launch data and plotting trajectories 
'''

import requests
import json
import pdb
import numpy as np
import csv 
import matplotlib.pyplot as plt
import math 


# returns lat, lon, altitude from xyz coordinates 
def get_lat_lon(x, y, z):
    # source: https://space.stackexchange.com/questions/17916/ground-longitude-latitude-under-a-satellite-cartesian-coordinates-at-a-specfic
    r = np.sqrt(x**2 + y**2 + z**2)

    # WGS-84 PARAMETERS, semimajor and semiminor axis
    a = 6378137.0
    b = 6356752.314 

    # Eccentricity
    e_squared = (a**2 - b**2) / a**2

    # Auxiliary quantities
    p = np.sqrt(x**2 + y**2)

    # Latitude (phi) & Longitude (lam)
    phi = np.rad2deg(np.arctan2(z, ((1- e_squared) * p)))
    lam = np.rad2deg(np.arctan2(y, x))

    # Radius of curvature in prime vertical               
    N = a / np.sqrt(1 - e_squared * (np.sin(np.deg2rad(phi)))**2)

    # Altitude
    h = (p / np.cos(np.deg2rad(phi))) - N

    return phi, lam, h


'''
PLOTS THE LAUNCH SITE COORDINATES 
'''
def plot_launch_site(data):
    launch_long = data[0]['mission']['initialConditions']['launchpad']['launchpad']['longitude']
    launch_lat = data[0]['mission']['initialConditions']['launchpad']['launchpad']['latitude']
    plt.plot(launch_long, launch_lat, marker='o', markersize=12)


'''
PLOTS THE LANDING SITE COORDINATES 
'''
def plot_landing_site(data):
    landing_long = data[0]['mission']['landingZones'][0]['longitude']
    landing_lat = data[0]['mission']['landingZones'][0]['latitude']
    plt.plot(landing_long, landing_lat, marker='o', markersize=12)


'''
PLOTS THE LAUNCH TRAJECTORY AND RETURNS THE ANGLE 
'''
def launch_trajectory(data, plot=True):
    # data comes in as JSON object 
    stageTrajectories = data[0]['data']['stageTrajectories']
    stage_index = None

    # find which index corresponds to the 1st stage of the rocket 
    for index, stage in enumerate(stageTrajectories):
        if stage['stageNumber'] == 1:
            stage_index = index
    
    # create numpy array of Nx3 where N = length of data for 1st stage and 3 = lat,long, height data 
    stage_LLH = np.empty((len(stageTrajectories[stage_index]['telemetry']), 3))
    max_altitude_index = 0

    # loop through 1st stage trajectory data and get the lat, long, heights
    for i in range(stage_LLH.shape[0]):
        # use x_NI, which is the non-inertial position
        x = stageTrajectories[stage_index]['telemetry'][i]['x_NI'][0]  # x
        y = stageTrajectories[stage_index]['telemetry'][i]['x_NI'][1]  # y
        z = stageTrajectories[stage_index]['telemetry'][i]['x_NI'][2]  # z 

        # latitude, longitude, altitude 
        stage_LLH[i][0], stage_LLH[i][1], stage_LLH[i][2] = get_lat_lon(x,y,z)
        
        # we can end the trajectory when we reach 60,000 ft (when FAA stops regulating airspace)
        if stage_LLH[i][2] > 18288: # in meters 
            max_altitude_index = i
            break
    
    # now add the distance to distances.txt
    with open('distances.txt', 'a') as f:
        start = [stageTrajectories[stage_index]['telemetry'][0]['x_NI'][0], stageTrajectories[stage_index]['telemetry'][0]['x_NI'][1]]
        end = [stageTrajectories[stage_index]['telemetry'][max_altitude_index]['x_NI'][0], stageTrajectories[stage_index]['telemetry'][max_altitude_index]['x_NI'][1]]
        f.write(str(math.dist(start, end)))
        f.write("\n")
        

    # plot only if requested 
    if plot:
        #print(np.max(stage_LLH[:max_altitude_index, 2]))
        #print(np.min(stage_LLH[:max_altitude_index, 2]))
        #plt.plot(stage_LLH[:,1], stage_LLH[:,0])

        # plot up to the max altitude index 
        plt.plot(stage_LLH[:max_altitude_index,1], stage_LLH[:max_altitude_index,0])

        # extras on plot 
        plot_launch_site(data)
        #plot_landing_site(data)
        plt.title("1st Stage Trajectory")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        #plt.show()

    # return launch angle 
    return np.arctan2(stage_LLH[-1,0] - stage_LLH[0,0], stage_LLH[-1,1] - stage_LLH[0,1])


'''
RETURNS ARRAY OF LAUNCH METRICS FOR 1 MISSION
["Company", "Vehicle", "Launchpad", "Pad Longitude", "Pad Latitude", "Launch Angle", "Launch Distance"]
'''
def get_launch_metrics(data):
    # data comes in as JSON object 
    stageTrajectories = data[0]['data']['stageTrajectories']
    stage_index = None

    # find which index corresponds to the 1st stage of the rocket 
    for index, stage in enumerate(stageTrajectories):
        if stage['stageNumber'] == 1:
            stage_index = index
    
    # create numpy array of Nx3 where N = length of data for 1st stage and 3 = lat,long, height data 
    stage_LLH = np.empty((len(stageTrajectories[stage_index]['telemetry']), 3))
    max_altitude_index = 0

    # loop through 1st stage trajectory data and get the lat, long, heights
    for i in range(stage_LLH.shape[0]):
        # use x_NI, which is the non-inertial position
        x = stageTrajectories[stage_index]['telemetry'][i]['x_NI'][0]  # x
        y = stageTrajectories[stage_index]['telemetry'][i]['x_NI'][1]  # y
        z = stageTrajectories[stage_index]['telemetry'][i]['x_NI'][2]  # z 

        # latitude, longitude, altitude 
        stage_LLH[i][0], stage_LLH[i][1], stage_LLH[i][2] = get_lat_lon(x,y,z)
        
        # we can end the trajectory when we reach 60,000 ft (when FAA stops regulating airspace)
        if stage_LLH[i][2] > 18288: # in meters 
            max_altitude_index = i
            break
    
    start = [stageTrajectories[stage_index]['telemetry'][0]['x_NI'][0], stageTrajectories[stage_index]['telemetry'][0]['x_NI'][1]]
    end = [stageTrajectories[stage_index]['telemetry'][max_altitude_index]['x_NI'][0], stageTrajectories[stage_index]['telemetry'][max_altitude_index]['x_NI'][1]]
    distance = math.dist(start, end)
    angle = np.arctan2(stage_LLH[-1,0] - stage_LLH[0,0], stage_LLH[-1,1] - stage_LLH[0,1])
    
   
    company = data[0]['mission']['company']['description']
    vehicle = data[0]['mission']['vehicle']['description']
    launchpad = data[0]['mission']['initialConditions']['launchpad']['launchpad']['description']
    pad_long = data[0]['mission']['initialConditions']['launchpad']['launchpad']['longitude']
    pad_lat = data[0]['mission']['initialConditions']['launchpad']['launchpad']['latitude']
    return [company, vehicle, launchpad, pad_long, pad_lat, angle, distance]

    
# plot the hazard zones as given by flightclub.io 
def show_hazard(data):

    #for zone in hazard_zones:  # use for loop for plotting all danger zones, comment out if just want 1st one  
    hazard_zones = data[0]['mission']['hazardZone']['zones'][0]
    hazard_vertices = hazard_zones['vertices']
    N = len(hazard_vertices)

    # get the vertices of the hazard zones - (N+1)x2 where N = number of vertices, 2 = lat,long
    vertices = np.empty((N+1, 2))
    for i in range(N):
        vertices[i][0] = hazard_vertices[i]['longitude']
        vertices[i][1] = hazard_vertices[i]['latitude']
    vertices[-1] = vertices[0]  # wrap around to complete the polygon

    plt.plot(vertices[:, 0], vertices[:, 1])
    plot_launch_site(data)

    plt.title("Hazard Zones")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    #plt.show()


# helper function to get the json simulation file for a mission
def get_JSON(URL, missionID):
    # make the request 
    params = {'missionId': missionID}
    authorization_header = {'X-Api-Key': 'apitn_khtv572bj'}
    r = requests.get(url = URL, params=params, headers=authorization_header)
    
    # quit if there was an error in the request 
    if (r.status_code != 200):
        print("error: status code:" + str(r.status_code))
        return r.status_code 
    
    # get data and put it in a json file 
    data = r.json()
    json_object = json.dumps(data, indent=2)
    with open('mission_files/' + missionID + '.json', 'w') as outfile: 
        outfile.write(json_object)
    
    return r.status_code


'''
USED FOR TESTING PURPOSES 
'''
def main():
    #pdb.set_trace()
    URL = 'https://api.flightclub.io/v3/simulation'
    missionID = 'mis_1mnfpyle4'

    #pdb.set_trace()
    # use this to get the json file if you dont have it saved already 
    error_code = get_JSON(URL, missionID)
    if (error_code != 200):
        return
    
    with open('mission_files/' + missionID + '.json', 'r') as openfile:
        data = json.load(openfile)
        #show_hazard(data)
        launch_trajectory(data)
        plt.show()
        
    
    
if __name__ == "__main__":
    main()
    
    