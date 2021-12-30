import math

import roadster.point as point

import shapely.geometry as sg


def test_distance():
    mapdata = [
        sg.LineString([(100, 100), (50, 50)]),
        sg.LineString([(10, 10), (20, 20)]),
    ]
    assert point.distance(mapdata, (0, 0)) == math.sqrt(2 * 10 ** 2)
    assert point.distance(mapdata, (20, 20)) == 0
    assert point.distance(mapdata, (21, 21)) == math.sqrt(2)
    assert point.distance(mapdata, (21, 20)) == 1
