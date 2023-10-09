'''
This code gets the missions from flightclub.io and puts them into missions.csv 
'''

import requests
import json
import pdb
import numpy as np
import csv 


def get_missions():
    
    # make the API request 
    URL = "https://api.flightclub.io/v3/mission/projected"
    #URL = "https://api.flightclub.io/v3/simulation?missionId=mis_173tkzsyn"
    authorization_header = {'X-Api-Key': 'apitn_khtv572bj'}
    r = requests.get(url = URL, headers=authorization_header)
    
    # exit if there was an error with the json request 
    if (r.status_code != 200):
        print("error: status code" + r.status_code)
        return

    data = r.json()

    # in missions.csv file create headers then pull data out of json objects into rows
    with open('missions.csv', 'w', newline='') as file: 
        writer = csv.writer(file)
        writer.writerow(["resourceID", "description", "startDateTime", "company", "vehicle"])
        for mission in data:
            writer.writerow([mission["resourceId"], mission["description"], mission["startDateTime"], mission["company"]["description"], mission["vehicle"]["description"]])
    
    # put the csv file into json format for readability
    json_object = json.dumps(data, indent=2)
    with open("missions.json", "w") as outfile: 
        outfile.write(json_object)


def main():
    get_missions()

if __name__ == "__main__":
    main()
    
    