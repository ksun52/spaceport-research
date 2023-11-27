import pdb
import os
import json
import numpy as np
import math
from enum import IntEnum

import rasterio
from rasterio.mask import mask, raster_geometry_mask

from shapely.geometry import Polygon
import matplotlib.pyplot as plt


class Side(IntEnum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


def main():
    # Open the GeoTIFF file
    file_directory = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(file_directory, 'usgrid_data_2010/geotiff/uspop10.tif')
    dataset = rasterio.open(filename)
    
    # Create a Polygon geometry for the flyover zone
    brevard_county = (-80.7012054832, 28.300314142)
    #test = (-96.977, 31.5)
    #hidalgo_county = (-98.18, 26.39)
    #monroe_county = (-87.36, 31.56)

    angle = 92   # launch angle convention
    angle2 = (90 - angle) % 360 # polar angle convention 
    #vertices = get_corners(hidalgo_county, angle2, 5, dataset)
    vertices = get_corners(brevard_county, angle2, spread=15, dataset=dataset)
    if not vertices:
        print("no")
        return    
    #pdb.set_trace()
    #for i in range(0,360,10):
    #vertices = get_corners(test, 90, i, dataset)
    flyover_polygon = Polygon(vertices)

    # population flown over 
    masked_image, masked_transform = mask(dataset, [flyover_polygon], all_touched=True, nodata=0, crop=False)
    print(np.sum(masked_image))

    # FOR PLOTTING PURPOSES 
    # transform (long, lat) into pixel coordinates (how far down, how far right) where (0,0) is top left
    pixel_coords = [dataset.index(vertex[0], vertex[1]) for vertex in vertices]
    # transform  pixel_coords into the convention for plt.plot which is (how far right, how far down)
    pixel_plot_coords = [(i[1], i[0]) for i in pixel_coords]
    flyover_polygon_pixels = Polygon(pixel_plot_coords)
    pdb.set_trace()
    # Plot the boundary on the GeoTIFF 
    plt.imshow(dataset.read(1), cmap='gray')
    plt.plot(*flyover_polygon_pixels.exterior.xy, color='red', linewidth=2)
    plt.show()
    print("end")

# new as of 10/8 - re-write find_trajectories2 to pre-find all of the angle slices then add them up:
# currently not using
def valid_angle(start_coord, launch_angle, spread, dataset):
    left_angle = (launch_angle + spread/2) % 360    # when standing at the point, looking out at the launch angle, this is on the left hand side
    right_angle = (launch_angle - spread/2) % 360

    # note: launch azimuth uses 0 degrees as north but intersection function uses 0 degrees pointing in positive x direction for cartesian coordinate system 
    left_coord, left_intersect = intersection(start_coord, left_angle, dataset)
    right_coord, right_intersect = intersection(start_coord, right_angle, dataset)

    # check if the intersection points violate flying over Mexico or Canada
    if into_mex_can(left_coord, left_intersect, right_coord, right_intersect):
        return False
    
    return True

# new as of 10/8 - re-write find_trajectories2 to pre-find all of the angle slices then add them up:
# currently not using
def all_angle_slices(start_coord, spread, dataset, mexico_mask):
    angle_info = {} # index i corresponds to the 1 degree slice starting on degree i or centered on degree i (with 0.5 degrees on either side)
    if spread % 2 == 0:
        left_angle = 1
        right_angle = 0
    else:
        left_angle = 0.5
        right_angle = -0.5 % 360 
    
    left = dataset.bounds.left
    right = dataset.bounds.right
    top = dataset.bounds.top
    bottom = dataset.bounds.bottom
    dataset_corners = [(right, top), (right, bottom), (left, bottom), (left, top)]
    
    for target in range(360):
        validSlice = True

        left_coord, left_intersect = intersection(start_coord, left_angle, dataset)
        right_coord, right_intersect = intersection(start_coord, right_angle, dataset)

        if into_mex_can(left_coord, left_intersect, right_coord, right_intersect):
            validSlice = False
        else:
            # clockwise with 0 index starting at top right corner 
            slice_corners = [start_coord, left_coord]    # first add the left coordinate and see if we need to add more corners 
            # if target == 189:
            #     breakpoint()
            # if target == 190:
            #     breakpoint()
            # go in a clockwise circle starting from the left intersect and add all the corners of the geotiff image 
            for i in range((int(right_intersect) - int(left_intersect)) % 4):
                add_corner = dataset_corners[(i + int(left_intersect)) % 4]
                slice_corners.append(add_corner)
            
            slice_corners.append(right_coord)

            flyover_slice = Polygon(slice_corners)


            # # FOR PLOTTING PURPOSES 
            # # transform (long, lat) into pixel coordinates (how far down, how far right) where (0,0) is top left
            # pixel_coords = [dataset.index(vertex[0], vertex[1]) for vertex in slice_corners]
            # # transform  pixel_coords into the convention for plt.plot which is (how far right, how far down)
            # pixel_plot_coords = [(i[1], i[0]) for i in pixel_coords]
            # flyover_polygon_pixels = Polygon(pixel_plot_coords)

            # # Plot the boundary on the GeoTIFF 
            # plt.imshow(dataset.read(1), cmap='gray')
            # plt.plot(*flyover_polygon_pixels.exterior.xy, color='red', linewidth=2)
            # print(target)
            # #plt.show()

            # do a secondary mexico flyover check with the created slice - if intersects mexico still, then not valid slice  
            # can be conservative and say all_touched = True for intersecting mexico 
            flyover_mask, _, _ = raster_geometry_mask(dataset, [flyover_slice], all_touched=True, invert=True, crop=False)
            if np.sum(np.multiply(mexico_mask, flyover_mask)) > 0:
                validSlice = False
            else:    
                # population flown over
                # alternate between all_touched=True and all_touched=False to avoid double counting edges 
                if target%2 == 0:
                    masked_image, _ = mask(dataset, [flyover_slice], all_touched=True, nodata=0, crop=False)
                else:
                    masked_image, _ = mask(dataset, [flyover_slice], all_touched=False, nodata=0, crop=False)
                
                
                pop = np.sum(masked_image)

        if not validSlice:
            angle_info[right_angle] = None
        else:
            angle_info[right_angle] = pop

        left_angle = (left_angle + 1) % 360
        right_angle = (right_angle + 1) % 360
    
    return angle_info






# start coords = tuple of (longitude, lattitude)
# launch_angle = which direction to launch towards
# spread = how wide the search cone should be (between 0 and 180 degrees)
# dataset = rasterio tiff file 
# returns list of tuples with the correct Polygon coordinates 
def get_corners(start_coord, launch_angle, spread, dataset):
    left_angle = (launch_angle + spread/2) % 360    # when standing at the point, looking out at the launch angle, this is on the left hand side
    right_angle = (launch_angle - spread/2) % 360

    # note: launch azimuth uses 0 degrees as north but intersection function uses 0 degrees pointing in positive x direction for cartesian coordinate system 
    left_coord, left_intersect = intersection(start_coord, left_angle, dataset)
    right_coord, right_intersect = intersection(start_coord, right_angle, dataset)


    left = dataset.bounds.left
    right = dataset.bounds.right
    top = dataset.bounds.top
    bottom = dataset.bounds.bottom

    # check if the intersection points violate flying over Mexico or Canada
    if into_mex_can(left_coord, left_intersect, right_coord, right_intersect):
        return None

    # clockwise with 0 index starting at top right corner 
    dataset_corners = [(right, top), (right, bottom), (left, bottom), (left, top)]
    polygon_corners = [start_coord, left_coord]    # first add the left coordinate and see if we need to add more corners 
    
    # go in a clockwise circle starting from the left intersect and add all the corners of the geotiff image 
    for i in range((int(right_intersect) - int(left_intersect)) % 4):
        add_corner = dataset_corners[(i + int(left_intersect)) % 4]
        polygon_corners.append(add_corner)

    # spread boundaries stretch behind the launch angle so just take all the corners
    if (right_intersect == left_intersect) and spread > 180:
        for i in range(4):
            add_corner = dataset_corners[(i + int(left_intersect)) % 4]
            polygon_corners.append(add_corner)
    
    polygon_corners.append(right_coord)
    return polygon_corners



def atan2_deg(y, x):
    return math.degrees(math.atan2(y, x))

def tan_deg(angle_in_degrees):
    return math.tan(math.radians(angle_in_degrees))
    
# check where the desired angle enclosure intersects the bounding box  
def intersection(start_coord, angle, dataset):
    left = dataset.bounds.left
    right = dataset.bounds.right
    top = dataset.bounds.top
    bottom = dataset.bounds.bottom

    x, y = start_coord

    missing_coord = None    # which level the intersection happens
    intersect = None    # the full intersection coordinate (longitude, latitude)
    intersect_side = None

    # corner angle - the angle between the line connecting corner and start coordinate with x axis
    # if the corner angle is larger than angle, then the bounding line will reach one side before it reaches the other side
    if 0 <= angle and angle < 90:
        corner_angle = atan2_deg(top - y, right - x)
        if angle == 0:
            intersect = (right, y)
            intersect_side = Side.RIGHT

        elif corner_angle > angle:
            # intersect at right edge 
            missing_coord = tan_deg(angle) * (right - x) + y
            intersect = (right, missing_coord)
            intersect_side = Side.RIGHT
        else:
            # intersect at top edge 
            missing_coord = (top - y) / tan_deg(angle) + x
            intersect = (missing_coord, top)
            intersect_side = Side.TOP
    elif 90 <= angle and angle < 180:
        corner_angle = atan2_deg(top - y, left - x)
        if angle == 90:
            intersect = (x, top)
            intersect_side = Side.TOP
        elif corner_angle > angle:
            # intersect at top edge 
            missing_coord = (top - y) / tan_deg(angle) + x
            intersect = (missing_coord, top)
            intersect_side = Side.TOP
        else:
            # intersect at left edge 
            missing_coord = tan_deg(angle) * (left - x) + y
            intersect = (left, missing_coord)
            intersect_side = Side.LEFT
    elif 180 <= angle and angle < 270:
        corner_angle = atan2_deg(bottom - y, left - x)
        if angle == 180: 
            intersect = (left, y)
            intersect_side = Side.LEFT
        elif corner_angle + 360 < angle:
            # intersect at bottom edge 
            missing_coord = (bottom - y) / tan_deg(angle) + x
            intersect = (missing_coord, bottom)
            intersect_side = Side.BOTTOM
        else:
            # intersect at left edge 
            missing_coord = tan_deg(angle) * (left - x) + y
            intersect = (left, missing_coord)
            intersect_side = Side.LEFT
            
    elif 270 <= angle and angle < 360:
        corner_angle = atan2_deg(bottom - y, right - x)
        if angle == 270:
            intersect = (x, bottom)
            intersect_side = Side.BOTTOM
        elif corner_angle + 360 < angle:
            # intersect at right edge 
            missing_coord = tan_deg(angle) * (right - x) + y
            intersect = (right, missing_coord)
            intersect_side = Side.RIGHT
        else:
            # intersect at bottom edge 
            missing_coord = (bottom - y) / tan_deg(angle) + x
            intersect = (missing_coord, bottom)
            intersect_side = Side.BOTTOM
    else:
        raise RuntimeError("no angle matches")

    return intersect, intersect_side
    

# If a boundary edge reaches the bottom of the geotiff image and is within
# a set longitude width, then the trajectory path would be over Mexico and
# the trajectory is not allowed.
# Similarly, if boundary edge reaches the top of the geotiff image and is
# within a set logitude witdh, then the trajectory path would be over Canada 

# Mexico boundary: within -117.2 and -93.5 degrees longitude on the bottom 
# border of the geotiff image 
# Canada boundary: anywhere on the top boundary is not allowed  
def into_mex_can(left_coord, left_intersect, right_coord, right_intersect):
    
    # intersects Canada from top 
    if left_intersect == Side.TOP or right_intersect == Side.TOP:
        return True 

    # intersects Canada from Maine 
    # left side intersects Canada from Maine (only need to check this, dont need to check right side)
    if left_intersect == Side.RIGHT and left_coord[1] > 44.79583:
        return True

    # right side boundary intersects Mexico 
    if right_intersect == Side.BOTTOM:
        if right_coord[0] > -117.2 and right_coord[0] < -93.5:
            return True
    
    # left side boundary intersects Mexico 
    if left_intersect == Side.BOTTOM:
        if left_coord[0] > -117.2 and left_coord[0] < -93.5:
            return True

    # right and left boundaries sandwich Mexico 
    if right_intersect == Side.BOTTOM and left_intersect == Side.BOTTOM:
        if left_coord[0] > -93.5 and right_coord[0] < -117.2:
            return True

    return False




if __name__ == "__main__":
    main()