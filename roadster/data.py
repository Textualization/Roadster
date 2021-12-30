import fiona
import shapely.geometry as sg
import multiprocessing
import numpy as np
import time
import random
import sys

import os.path

from skimage.io import imsave, imread
from skimage import img_as_ubyte
from skimage.draw import line as skline


def load_map(map_file: str, road_layer: int = 0, road_type: set = set(["all"])):
    """Load the geometry objects in a given layer from a compressed shape file."""
    if map_file.endswith(".shp.zip"):
        fname = f"zip://{map_file}"
    else:
        fname = f"zip://download/{map_file}.shp.zip"

    with fiona.open(fname, layer=road_layer) as src:
        if "all" in road_type:
            mapdata = [sg.shape(obj["geometry"]) for obj in src]
        else:
            mapdata = [
                sg.shape(obj["geometry"])
                for obj in src
                if obj["properties"]["fclass"] in road_type
            ]
    return mapdata


def list_layers(map_file: str):
    """List layers in file, together with their size."""
    if map_file.endswith(".shp.zip"):
        fname = f"zip://{map_file}"
    else:
        fname = f"zip://download/{map_file}.shp.zip"
    result = list()
    for idx, layername in enumerate(fiona.listlayers(fname)):
        with fiona.open(fname, layer=idx) as src:
            result.append((idx, layername, len(src)))
    return result


def create_image(tile_width: int, tile_height: int):
    """Create a grayscale, floating point image of given width and height."""
    return np.zeros((tile_height, tile_width))


def pre_filter(mapdata: list, ul: tuple, lb: tuple, multiplier=2.5):
    """Prefilter the data to only include roads within a multiplier radious from the tile."""
    ul_p = sg.Point(*ul)
    lb_p = sg.Point(*lb)

    gps_w = lb[0] - ul[0]
    gps_h = lb[1] - ul[1]

    max_d = max(abs(multiplier * gps_w), abs(multiplier * gps_h))

    result = list()
    for obj in mapdata:
        ul_d = obj.distance(ul_p)
        lb_d = obj.distance(lb_p)
        if min(ul_d, lb_d) < max_d:
            result.append(obj)
    return result


def plot_roads(image: np.ndarray, mapdata: list, ul: tuple, lb: tuple, road_value=1.0):
    """Draw the roads that lie within a given tile, the roads are set to road_value."""
    h, w = image.shape

    ul_p = sg.Point(*ul)
    lb_p = sg.Point(*lb)

    gps_w = lb[0] - ul[0] * 1.0
    gps_h = lb[1] - ul[1] * 1.0

    w_dot = gps_w / w
    h_dot = gps_h / h

    def coord2px(c):
        x = (c[0] - ul[0]) * 1.0 / w_dot
        y = (c[1] - ul[1]) * 1.0 / h_dot

        x, y = y, x

        return (max(0, min(int(x), h - 1)), max(0, min(int(y), w - 1)))

    tile = sg.Polygon([ul, (ul[0], lb[1]), lb, (lb[0], ul[1])])
    chopped = list()
    for obj in mapdata:
        if tile.intersects(obj):
            chopped.append(obj.intersection(tile))
    for curve in chopped:
        ls = list()
        if curve.type == "GeometryCollection" or curve.type == "MultiLineString":
            ls = [part for part in curve.geoms]
        elif curve.type == "LineString":
            ls = [curve]
        elif curve.type == "Point":
            ls = []  # ignore
        else:
            ls = []
            print("missing type", curve.type)
        for cc in ls:
            ps = list(cc.coords)
            prev = ps[0]
            ps = ps[1:]
            prev = coord2px(prev)
            for curr in ps:
                curr = coord2px(curr)
                rr, cc = skline(*prev, *curr)
                image[rr, cc] = road_value
                prev = curr


def boost(image: np.ndarray, level=1000.0):
    """Boost the signal by `level` multiplier, if the signal saturates it is cap at 1.0."""
    image *= level
    image[image > 1.0] = 1.0
    image[image < 0.0] = 0.0


def save_image(image: np.ndarray, output_file: str):
    """Save the image as a greyscale 8-bit."""
    imsave(output_file, img_as_ubyte(image))
