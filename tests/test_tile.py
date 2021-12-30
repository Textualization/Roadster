import math

import roadster.tile as tile

import numpy as np
import shapely.geometry as sg

from skimage import img_as_ubyte
from skimage.io import imread


def test_plot_brute():
    img = np.zeros((200, 100), dtype=float)
    mapdata = [
        sg.LineString([(100, 100), (50, 50)]),
        sg.LineString([(10, 10), (20, 20)]),
    ]
    tile.plot(img, mapdata, "brute", (0, 0), (100, 200), boost=0.01)
    assert abs(img[0, 0] - math.sqrt(2 * 10 ** 2) / 100) < 1e10
    assert img[20, 20] == 0
    assert abs(img[21, 21] - math.sqrt(2) / 100) < 1e10
    assert abs(img[21, 20] - 1 / 100) < 1e10


def test_plot_kriging():
    img = np.zeros((200, 100), dtype=float)
    mapdata = [
        sg.LineString([(100, 100), (50, 50)]),
        sg.LineString([(10, 10), (20, 20)]),
    ]
    tile.plot(
        img, mapdata, "kriging", (0, 0), (100, 200), boost=0.01, seed=2, points=200
    )
    assert abs(img[0, 0] - math.sqrt(2 * 10 ** 2) / 100) < 1e10
    assert abs(img[20, 20]) < 1e10
    assert abs(img[21, 21] - math.sqrt(2) / 100) < 1e10
    assert abs(img[21, 20] - 1 / 100) < 1e10
