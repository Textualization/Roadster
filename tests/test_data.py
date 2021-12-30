import tempfile
import os

import roadster.data as data

import numpy as np
import shapely.geometry as sg

from skimage import img_as_ubyte
from skimage.io import imread


def test_load():
    mapdata = data.load_map("prince-edward-island-latest-free")
    assert len(mapdata) == 24866
    mapdata = data.load_map("prince-edward-island-latest-free", 11)
    assert len(mapdata) == 22243
    mapdata = data.load_map("prince-edward-island-latest-free", 11, set(["primary"]))
    assert len(mapdata) == 476


def test_list():
    layers = data.list_layers("prince-edward-island-latest-free")
    print(layers)
    assert len(layers) == 18
    assert layers[0][0] == 0
    assert layers[11][1] == "gis_osm_roads_free_1"
    assert layers[11][2] == 22243


def test_create():
    img = data.create_image(100, 10)
    assert len(img.shape) == 2
    assert img.shape[0] == 10
    assert img.shape[1] == 100
    assert img.dtype is np.dtype("float")


def test_filter():
    mapdata = [
        sg.LineString([(100, 100), (50, 50)]),
        sg.LineString([(10, 10), (20, 20)]),
    ]
    filtered = data.pre_filter(mapdata, (30, 0), (0, 30), 1.0)
    assert len(filtered) == 1
    assert filtered[0].coords[0] == (10, 10)


def test_plot():
    img = np.zeros((200, 100), dtype=float)
    mapdata = [
        sg.LineString([(100, 100), (50, 50)]),
        sg.LineString([(10, 10), (20, 20)]),
    ]

    data.plot_roads(img, mapdata, (0, 0), (100, 200))
    assert img[100, 99] == 1.0
    assert img[50, 50] == 1.0
    assert img[0, 0] == 0.0


def test_boost():
    img = np.zeros((200, 100), dtype=float)
    img[50, 50] = 0.01
    data.boost(img)
    assert img[0, 0] == 0
    assert img[50, 50] == 1


def test_save():
    img = np.zeros((200, 100), dtype=float)
    img[:50, :] = 1.0
    _, fname = tempfile.mkstemp(suffix=".png")
    data.save_image(img, fname)
    img2 = imread(fname)
    assert np.all(img == img2 / 255.0)
    os.unlink(fname)
