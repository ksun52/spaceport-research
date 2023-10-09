import pdb
import rasterio
from rasterio.mask import mask, raster_geometry_mask
from shapely.geometry import Polygon
import os
import matplotlib.pyplot as plt
import numpy as np
import json
import fiona
from pop_flown_over import get_corners

# Open the GeoTIFF file
file_directory = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
dataset = rasterio.open(filename)

# # test using a texas geojson file 
# with open(os.path.join(file_directory, 'geoJSON/sonora.geojson')) as data_file:
#     geoms = json.loads(data_file.read())

# coords = geoms['geometry']


# the mexico state part 
with fiona.open(os.path.join(file_directory, "mexico/mexican-states.shp"), 'r') as shapefile:
    shapes = [feature["geometry"] for feature in shapefile]

masked_image1, masked_transform1 = mask(dataset, shapes, all_touched=True, nodata=0, crop=False)    # with mexico state
masked1, _, _ = raster_geometry_mask(dataset, shapes, all_touched=True, invert=True, crop=False)
# print(masked)
# print(np.sum(masked))

 # Create a Polygon geometry for the flyover zone
#brevard_county = (-80.7012054832, 28.300314142)
#test = (-96.977, 31.5)
hidalgo_county = (-98.18, 26.39)

angle = 0   # launch angle convention
angle2 = (90 - angle) % 360 # polar angle convention 
vertices = get_corners(hidalgo_county, angle2, spread=10, dataset=dataset)
if not vertices:
    print("no")
    pdb.set_trace()

flyover_polygon = Polygon(vertices)

# population flown over 
masked_image2, masked_transform2 = mask(dataset, [flyover_polygon], all_touched=True, nodata=0, crop=False)
masked2, _, _ = raster_geometry_mask(dataset, [flyover_polygon], all_touched=True, invert=True, crop=False)
#print(np.sum(masked_image))

print(np.sum(np.multiply(masked1, masked2)))

# Close the dataset
dataset.close()

# Retrieve the pixel values within the triangle
# pixel_values = masked_image[0]
# print(np.sum(pixel_values))
# print("Pixel values within the triangle region:", pixel_values)
# print("masked_transform", masked_transform)
# print("num_features", len(shapes))
