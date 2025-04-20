import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import geopandas as gpd
import geoplot as gplt
import geopy.distance as distance
import math
from math import sin, cos, sqrt, atan2, radians
from mpl_toolkits.basemap import Basemap



### distance matrix helper function
def get_distance(lat1,lon1,lat2,lon2):

    # Approximate radius of earth in km
    radius = 6373.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    
    return d / 1.6

def get_dist_matrix(geoData):
    geo_ids = geoData["geo_id"].values
    center_lons = geoData["center_lon_x"].apply(lambda x : float(x)).values
    center_lats = geoData["center_lat_x"].apply(lambda x : float(x)).values
    dist_matrix = np.zeros((len(center_lons),len(center_lats)))
    for row_id in range(len(geo_ids)):
        curr_row_lon = center_lons[row_id]
        curr_row_lat = center_lats[row_id]
        for col_id in range(len(geo_ids)):
            curr_col_lon = center_lons[col_id]
            curr_col_lat = center_lats[col_id]
            dist_matrix[row_id][col_id] = get_distance(curr_row_lat,curr_row_lon,curr_col_lat,curr_col_lon)
    return dist_matrix

### DataFrame normalize function

def normalize(df):
    normalized_df=(df-df.min())/(df.max()-df.min())
    return normalized_df

### spfl gurobipy solver
def sflp(K,cand_ids,C_t,N,M,C_O,C_R,launch_cost):
    ### With distance constraint
    m = gp.Model('spaceport location planning')
    
    # Decision Variables
    
    # filtering 
    
    cand_counties = cand_ids
    
    x = m.addVars(len(cand_counties), vtype=GRB.BINARY,name = "x")
    y = m.addMVar((len(cand_counties),M), vtype=GRB.BINARY,name = "y")
    
    for idx in range(len(cand_counties)):
        i = cand_counties[idx]
        for j in range(M):
            m.addConstr((1/M) * gp.quicksum(y[idx][j] for j in range(M)) <= x[idx])
            m.addConstr(x[idx] <= gp.quicksum(y[idx][j] for j in range(M)))
                        
    m.addConstr(gp.quicksum(x[i] for i in range(len(cand_counties))) == K)
    
    m.setObjective(gp.quicksum((C_t[cand_counties[i]] + C_O[cand_counties[i]] + C_R[cand_counties[i]])*x[i] for i in range(len(cand_counties)))\
                   + gp.quicksum(launch_cost[i][j]*y[i][j] for i in range(len(cand_counties)) for j in range(M)),GRB.MINIMIZE)
    m.optimize()
    return m

### plot function
def plot_trj(longs,lats):
    fig = plt.figure(figsize=(12,8))
    m = Basemap(llcrnrlon = -128, llcrnrlat = 22.5, urcrnrlon = -63, urcrnrlat = 50, projection='merc')
    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)
    m.drawstates(linewidth=0.2)
    xpt,ypt=m(longs,lats)
    m.scatter(xpt,ypt,linewidth=1,color='r',marker = 'o')
    plt.show()


class SPFL():

    def __init__(self):

        """
        Initialize the SPFL class
        """
        self.K = None
        self.D = None
        self.C_T = None
        self.C_O = None
        self.C_R = None
        self.N = None
        self.M = None
        self.launch_arr = None
        self.conn = None
        self.dist_matrix = None
        self.res = None

    def set_parameters(self,K,D,C_T,C_O,C_R,N,M,launch_arr,dist_matrix,conn,W_T,W_O,W_R,W_L):

        self.K = K
        self.D = D
        self.C_T = W_T*C_T
        self.C_O = W_O*C_O
        self.C_R = W_R*C_R
        self.N = N
        self.M = M
        self.launch_arr = W_L * launch_arr
        self.dist_matrix = dist_matrix
        self.conn = conn

    def solve(self):

        res = []
        res_y = []
        missions = []
        mission_type = None
        cands = np.arange(self.N)
        cand = cands
        while len(res) < self.K:
            curr_m = sflp(1,cand,self.C_T,self.N,self.M,\
                self.C_O,self.C_R,self.launch_arr)
            x = [x.X for x in curr_m.getVars() if x.VarName.find("x") != -1]
            x = np.array(x)
            y = [x.X for x in curr_m.getVars() if x.VarName.find("y") != -1]
            mission_type = np.array(y).reshape((len(cand),M))
            missions.append(np.where(mission_type == 0)[1][0])
            curr_best_id = np.where(x==1)[0][0]
            original_best_id = cand[curr_best_id]
            res.append(original_best_id)
            #update cand
            for r in res:
                cand = [x for x in cand if x != original_best_id and self.dist_matrix[x][r] >= self.D]
        self.res = res

        return res, missions
    
    def plot_result(self):

        lons = []
        lats = []

        for idx in self.res:
            lon = self.conn.loc[idx]["center_lon_x"]
            lat = self.conn.loc[idx]["center_lat_x"]
            lons.append(lon)
            lats.append(lat)

        plot_trj(lons,lats)


if __name__ == "__main__":

    costs = pd.read_csv('cost.csv')
    costs = normalize(costs)

    conn = pd.read_csv('candidates.csv')
    conn2 = pd.read_csv('conn_df.csv')

    launch_cost = pd.read_csv('launch_cost.csv')
    launch_cost = normalize(launch_cost)
    
    #traffic_count = pd.read_csv('traffic_count.csv'

    dist_matrix = get_dist_matrix(conn2)

    N = len(conn2)

    M = len(launch_cost.columns)

    C_T = costs['C_t'].values
    C_O = costs['C_o'].values
    C_R = costs['C_r'].values

    unit_cost_R = 293

    m = SPFL()

    m.set_parameters(6,300,C_T,C_O,C_R,N,M,launch_cost.values,dist_matrix,conn2,1,1,1,100)

    res,res_y = m.solve()

    m.plot_result()

    traff_count = []

    for cand_id in res:
        traff_count.append(conn2.iloc[cand_id]['count'])

    
    cost_R = unit_cost_R * np.array(traff_count)

    print("Slected counties are \n")
    print("------------------------------------------")
    print([conn2.iloc[x]["county_name"] for x in res])
    print("------------------------------------------")

    print("---------------Mission types---------------------------")
    print(res_y)
    print("------------------------------------------")

    print("------------Reouting Cost-----------------------------")
    print(cost_R)
    print("------------------------------------------")







    













