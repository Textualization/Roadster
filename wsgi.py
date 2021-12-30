import os
import threading

from flask import Flask, request, make_response

import roadster

import imageio as iio
from skimage import img_as_ubyte

app = Flask(__name__)

threadLocal = threading.local()


def get_mapdata(mapname, road_layer):
    global threadLocal

    road_type = request.args.get("road_type", "all")
    mapstr = f"{mapname}:{road_layer}:{road_type}"
    maps = getattr(threadLocal, "maps", None)
    if maps is None:
        maps = dict()
        threadLocal.maps = maps
    if mapstr not in maps:
        mapdata = roadster.data.load_map(mapname, road_layer, set([road_type]))
        print(f"loaded {mapstr}")
        maps[mapstr] = mapdata
    else:
        mapdata = maps[mapstr]

    return mapdata


@app.route(
    "/tile/<mapname>/<int:road_layer>/<int:tile_width>/<int:tile_height>/<wnlat>/<wnlon>/<eslat>/<eslon>"
)
def tile(mapname, road_layer, tile_width, tile_height, wnlat, wnlon, eslat, eslon):
    mapdata = get_mapdata(mapname, road_layer)

    wnlat = float(wnlat)
    wnlon = float(wnlon)
    eslat = float(eslat)
    eslon = float(eslon)

    print(tile_width, tile_height)

    zero_roads = request.args.get("zero_roads", False)
    type_ = request.args.get("type", "auto")
    samples = float(request.args.get("samples", 0.01))
    boost = float(request.args.get("boost", 1000.0))
    image = roadster.data.create_image(tile_width, tile_height)
    roadster.tile.plot(
        image,
        mapdata,
        type_,
        (wnlon, wnlat),
        (eslon, eslat),
        points=samples,
        boost=boost,
    )
    roadster.data.plot_roads(
        image,
        mapdata,
        (wnlon, wnlat),
        (eslon, eslat),
        road_value=0.0 if zero_roads else 1.0,
    )

    print("generated")

    image_binary = iio.imwrite("<bytes>", img_as_ubyte(image), format="PNG")
    response = make_response(image_binary)
    response.headers.set("Content-Type", "image/png")
    return response


@app.route("/point/<mapname>/<int:road_layer>/<lat>/<lon>")
def point(mapname, road_layer, lat, lon):
    mapdata = get_mapdata(mapname, road_layer)

    return str(roadster.point.distance(mapdata, (float(lon), float(lat))))


@app.route("/")
def hello():
    return "hello"
