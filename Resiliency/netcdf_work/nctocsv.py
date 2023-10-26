import netCDF4 as nc
import pandas as pd

# Open the NetCDF file in read mode
file_path = 'Resiliency/risk_data/alltornadoes.nc'
data = nc.Dataset(file_path, 'r')

# Get latitude, longitude, and data variables
lat = data.variables['lat'][:]
lon = data.variables['lon'][:]
variable_name = 'alltorn'
variable_data = data.variables[variable_name][:]

# Create a DataFrame with latitude, longitude, and data
df = pd.DataFrame({
    'Latitude': lat.flatten(),
    'Longitude': lon.flatten(),
    'Data': variable_data.flatten()
})

# Save the DataFrame to a CSV file
csv_file_path = 'Resiliency/risk_data/alltornadoes.csv'
df.to_csv(csv_file_path, index=False)

# Close the NetCDF file
data.close()

print(f'Data has been saved to {csv_file_path}')
