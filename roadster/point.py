import numpy as np
import time
import random

import roadster.data as data

import shapely.geometry as sg


def distance(mapdata: list, point: tuple):
    """Distance to the closest road."""
    point = sg.Point(*point)
    return min([point.distance(obj) for obj in mapdata])
