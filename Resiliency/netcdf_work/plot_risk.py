import netCDF4 as nc
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pdb
import geopandas as gpd

# Open the NetCDF file in read mode
file_path = 'Resiliency/alltornadoes.nc'
data = nc.Dataset(file_path, 'r')

# Get the latitude and longitude data
lat = data.variables['lat'][:]
lon = data.variables['lon'][:]

# Get the variable data you want to visualize (e.g., temperature)
variable_name = 'alltorn'
variable_data = data.variables[variable_name][:]

# Create a map plot using Cartopy
plt.figure(figsize=(10, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# Plot the variable data on the map
plt.contourf(lon, lat, variable_data, transform=ccrs.PlateCarree())


# Add map features (borders, coastlines, etc.)
# pdb.set_trace()
# ax.coastlines()   # doesnt work due to SSL certificate error
shapefile_path = 'Resiliency/ne_50m_coastline/ne_50m_coastline.shp'

ax.gridlines(draw_labels=True)
# Read the shapefile using geopandas
gdf = gpd.read_file(shapefile_path)
# Plot the shapefile using matplotlib
gdf.plot(ax=ax)

# Set plot title and labels
plt.xlim(-150, -50)
plt.ylim(10,60)
plt.title(f'{variable_name} Data')
plt.xlabel('lons')
plt.ylabel('lats')

# Show the plot
plt.show()

# Close the NetCDF file
data.close()
