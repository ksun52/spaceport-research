import rasterio
import os
import numpy as np

# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)


# Read the dataset's valid data mask as a ndarray.
mask = dataset.dataset_mask()

# Extract feature shapes and values from the array.
for geom, val in rasterio.features.shapes(mask, transform=dataset.transform):

    # Transform shapes from the dataset's own coordinate
    # reference system to CRS84 (EPSG:4326).
    geom = rasterio.warp.transform_geom(
        dataset.crs, 'EPSG:4326', geom, precision=6)

    # Print GeoJSON shapes to stdout.
    print(geom)

# Define the coordinate
longitude = 10.123  # Replace with the desired longitude coordinate
latitude = 50.456   # Replace with the desired latitude coordinate

# Convert the coordinate to pixel coordinates
row, col = dataset.index(longitude, latitude)

# Get the geotransform and metadata
geotransform = dataset.transform
metadata = dataset.meta

print(np.sum(dataset.read(1) * dataset.read_masks(1)))   # get sum of all valid data in rasterio 

# Close the dataset
dataset.close()

# Print the geotiff information
print("Pixel coordinates (row, col):", row, col)
print("Geotransform:", geotransform)
print("Metadata:", metadata)