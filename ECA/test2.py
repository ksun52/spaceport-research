import rasterio
from rasterio.mask import mask
from shapely.geometry import Polygon
import os
import matplotlib.pyplot as plt
import numpy as np
import json

# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)

# test using a texas geojson file 
with open(os.path.join(file_directory, 'geoJSON/maryland.geojson')) as data_file:
    geoms = json.loads(data_file.read())
print(type(geoms))
coords = geoms['geometry']

# print bounds
print(dataset.bounds)

# Define the triangle vertices (example)
triangle_vertices = [(-86.861862, 41.734059), (-86.160376, 45.723671), (-82.021605, 45.392131), (-82.951075, 41.563703)]
# triangle_vertices = [(-100, 30), (-100, 45), (-80, 30)]

# Create a Polygon geometry for the triangle
triangle_polygon = Polygon(triangle_vertices)

# rectangle covering whole area 
left = dataset.bounds.left
right = dataset.bounds.right
top = dataset.bounds.top
bot = dataset.bounds.bottom

# RASTERIO CONVENTION IS (X, Y) OR (LONGITUDE, LATITUDE) COORDINATES 
whole = Polygon([(left, top), (left, bot), (right, bot), (right, top)])

# Plot the triangle on the GeoTIFF (optional)
# plt.imshow(dataset.read(1), cmap='gray')
# plt.plot(*triangle_polygon.exterior.xy, color='red', linewidth=2)
# plt.show()

# Mask the raster within the triangle
#masked_image, masked_transform = mask(dataset, [triangle_polygon], all_touched=True, nodata=0, crop=False)
#masked_image, masked_transform = mask(dataset, [coords], all_touched=True, nodata=0, crop=False)    # with texas 
masked_image, masked_transform = mask(dataset, [whole], all_touched=True, nodata=0, crop=False)    # with whole area

# Retrieve the pixel values within the triangle
pixel_values = masked_image[0]

# Close the dataset
dataset.close()

print("Pixel values within the triangle region:", pixel_values)
