'''
This code plots all launch trajectories from flightclub.io 
'''

import requests
import json
import pdb
import numpy as np
import csv 
import matplotlib.pyplot as plt
import os 
from sklearn.neighbors import KernelDensity

from common import get_lat_lon, launch_trajectory, get_launch_metrics

# gets a list of all mission IDs
def missions_list():
    missions = []   # has all the mission IDs
    with open('missions.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            missions.append(row[0])
    del missions[0]
    return missions

# get all launch sites (i.e. Cape Canaveral)
# missions = list of mission IDs
def find_launch_sites(missions):
    launch_sites = set()    # create set 

    # loop through all missionIDs in missions
    for missionID in missions:
        path = 'mission_files/' + missionID + '.json'
        
        # open up the mission and retrieve the launch site 
        if os.path.isfile(path):
            with open(path, 'r') as openfile:
                data = json.load(openfile)
                
                # skip if the mission json file is empty (just shows [])
                if len(data) == 0:
                    continue 
                else:
                    launch_sites.add(data[0]['mission']['initialConditions']['launchpad']['launchpad']['description'])
    return launch_sites

# plots all launch trajectories for each launch site 
# missions = list of mission IDs
# launch_sites = set of launch sites 
def plot_all_launches(missions, launch_sites):
    sites_list = list(launch_sites)

    # loop through all missions
    for missionID in missions:
        path = 'mission_files/' + missionID + '.json'
        
        if os.path.isfile(path):
            with open(path, 'r') as openfile:
                data = json.load(openfile)
                
                # skip if the mission json file is empty (just shows [])
                if len(data) == 0:
                    continue 
                else:
                    # set plot figure to the one corresponding to this launch site 
                    site = data[0]['mission']['initialConditions']['launchpad']['launchpad']['description']
                    site_idx = sites_list.index(site)
                    plt.figure(site_idx)
                    launch_trajectory(data) # plots launch trajectory on the current figure

    # add descriptions to figures
    for i in range(len(sites_list)):
        plt.figure(i)
        plt.title("1st Stage Trajectory of %s" % sites_list[i])
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
    plt.show()

'''
# this one is just a test to see how it works 
def plot_CC(missions):
    for missionID in missions:
        path = 'mission_files/' + missionID + '.json'
        
        if os.path.isfile(path):
            with open(path, 'r') as openfile:
                data = json.load(openfile)
                if len(data) == 0 or (data[0]['mission']['initialConditions']['launchpad']['launchpad']['description'] != 'SLC-41, Cape Canaveral' or data[0]['mission']['initialConditions']['launchpad']['launchpad']['description'] != 'SLC-41, Cape Canaveral'):
                    continue 
                else:
                    launch_trajectory(data)
    
    plt.title("1st Stage Trajectory")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()
'''

# get a distribution of the launch angles for launches in the US 
# missions = list of mission IDs
def US_probability_dist(missions):
    angles = np.array([])

    for missionID in missions:
        path = 'mission_files/' + missionID + '.json'
        
        if os.path.isfile(path):
            with open(path, 'r') as openfile:
                data = json.load(openfile)

                # skip if data is empty or launch is not in US 
                if len(data) == 0 or data[0]['mission']['initialConditions']['launchpad']['launchpad']['country'] != 'US':
                    continue 
                else:
                    angles = np.append(angles, launch_trajectory(data, plot=False)) # dont plot but just get the angle 
    # returns numpy array of launch angles 
    return angles


# create CSV file that has company, vehicle, launchpad, pad longitude, pad latitude, launch angle, launch distance 
def launch_metrics(missions):

    with open('launch_metrics.csv', 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(["Company", "Vehicle", "Launchpad", "Pad Longitude", "Pad Latitude", "Launch Angle", "Launch Distance"])

        for missionID in missions:
            path = 'mission_files/' + missionID + '.json'
            
            if os.path.isfile(path):
                with open(path, 'r') as openfile:
                    data = json.load(openfile)

                    # skip if data is empty or launch is not in US 
                    if len(data) == 0 or data[0]['mission']['initialConditions']['launchpad']['launchpad']['country'] != 'US':
                        continue 
                    else:
                        writer.writerow(get_launch_metrics(data))
    

def main():
    missions = missions_list()
    #launch_sites = find_launch_sites(missions)
    #print(launch_sites)

    #plot_all_launches(missions, launch_sites)
    launch_metrics(missions)

    '''launch_angles = US_probability_dist(missions)[:, None]
    print(launch_angles)
    #pdb.set_trace()
    model = KernelDensity(bandwidth=1, kernel="gaussian")
    model.fit(launch_angles)
    log_dens = model.score_samples(launch_angles)
    pdb.set_trace()
    plt.figure(1)
    plt.fill(launch_angles, np.exp(log_dens))
    '''
    
   

    #plt.show()
    

if __name__ == "__main__":
    main()