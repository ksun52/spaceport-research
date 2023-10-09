'''
This code gets all simulations from flightclub.io in the form of json files and saves them
Known issue: a lot of simulations are blank - all they show is "[]"
'''

import requests
import json
import pdb
import numpy as np
import csv 
import matplotlib.pyplot as plt
import os 

from common import get_JSON
from get_missions import get_missions


def main():
    get_missions()  # run this to get updated missions.csv and missions.json (comment out if already have the most updated)

    # first get all the mission IDs that we need to retrieve 
    missions = []   # has all mission IDs
    with open('missions.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            missions.append(row[0])    
    del missions[0] # first line is just the headers for missions.csv so we can delete it  


    # SUPER SLOW - CHECK IF YOU HAVE ALREADY RETRIEVED THE JSON DATA BEFORE PULLING IT
    URL = 'https://api.flightclub.io/v3/simulation'
    for missionID in missions:
        if not os.path.exists('mission_files/' + missionID + '.json'):  # check if you already have it
            get_JSON(URL, missionID)


if __name__ == "__main__":
    main()