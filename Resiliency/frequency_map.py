import geopandas as gpd
import pandas as pd
import pdb 
from shapely import wkt
import matplotlib.pyplot as plt
import json

graphic_file = '/Users/kevin/Desktop/Research/CODE/ECA/graphic.csv'

df = pd.read_csv(graphic_file)
df['geometry'] = df['geometry'].apply(wkt.loads)


# add additional info from annual frequencies to graphic.csv
import json

# Load data from the JSON file
with open('/Users/kevin/Desktop/Research/CODE/Resiliency/annual_frequencies.json', 'r') as file:
    data = json.load(file)

# gather all the annualized frequency info
flood_af = []
earthquake_af = []
hail_af = []
hurricane_af = []
ice_storm_af = []
lightning_af = []
strong_wind_af = []
tornado_af = []
for county in data:
    flood_af.append(county["coastal_flooding"])
    earthquake_af.append(county["earthquake"])
    hail_af.append(county["hail"])
    hurricane_af.append(county["hurricane"])
    ice_storm_af.append(county["ice_storm"])
    lightning_af.append(county["lightning"])
    strong_wind_af.append(county["strong_wind"])
    tornado_af.append(county["tornado"])

# pdb.set_trace()

df['flood_af'] = flood_af
df['earthquake_af'] = earthquake_af
df['hail_af'] = hail_af
df['hurricane_af'] = hurricane_af
df['ice_storm_af'] = ice_storm_af
df['lightning_af'] = lightning_af
df['strong_wind_af'] = strong_wind_af
df['tornado_af'] = tornado_af


gdf = gpd.GeoDataFrame(df, geometry='geometry')

hazards = [("flood_af", "Coastal Flooding"), ("earthquake_af", "Earthquake"), ("hail_af", "Hail"), ("hurricane_af", "Hurricane"), ("ice_storm_af", "Ice Storm"), ("lightning_af", "Lightning"), ("strong_wind_af", "Strong Wind"), ("tornado_af", "Tornado")]

for i in range(8):
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    gdf.plot(column = hazards[i][0], cmap='Reds', linewidth=0.1, edgecolor='gray', ax=ax, legend=True, legend_kwds={'shrink': 0.66})
    ax.set_title(f'{hazards[i][1]} Annualized Frequency', fontdict={'fontsize': '18', 'fontweight': '3'})
    ax.tick_params(axis='both', which='major', labelsize=14)

    plt.show()


# gdv.plot(column = "population",scheme='percentiles',cmap='Blues')