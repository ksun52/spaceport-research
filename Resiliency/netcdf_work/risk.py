import netCDF4 as nc

# Open the NetCDF file in read mode
file_path = 'alltornadoes.nc'
data = nc.Dataset(file_path, 'r')

# Access variables and dimensions in the NetCDF file
print("Variables:", data.variables.keys())  # Print variable names
print("Dimensions:", data.dimensions.keys())  # Print dimension names
# print(data.dimensions.values())

# Read data from a specific variable
variable_name = 'lon'
variable_data = data.variables[variable_name][:]  # This reads the entire variable data
print(f"Data from {variable_name} variable:")
# print(variable_data)

nc.ncdump(data)

# Close the NetCDF file
data.close()
