import sys
import argparse

import roadster.data as data
import roadster.tile as tile
import roadster.point as point


def add_base_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-m",
        "--map",
        type=str,
        help="Map suffix, e.g., `malta-latest-free`, the `.shp.zip` extension is added. This file is searched for in `download` folder. If the parameter contains a file path, the file is used verbatim (and needs to include the extension).",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--road_layer",
        type=int,
        help="Layer that contains the road information.",
        default=0,
    )
    parser.add_argument(
        "-r",
        "--road_type",
        type=str,
        help="Type of roads (e.g., 'primary'), by default use all roads.",
        default="all",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action=argparse.BooleanOptionalAction,
        help="Print extra information to console.",
    )


def load_map(args: argparse.Namespace):
    return data.load_map(args.map, args.road_layer, set([args.road_type]))


def one_tile():
    parser = argparse.ArgumentParser(
        description="Compute the distance-to-closest-road for all pixels in a tile.",
        add_help=False,
    )
    add_base_args(parser)
    parser.add_argument(
        "-z",
        "--zero_roads",
        action=argparse.BooleanOptionalAction,
        help="Set road distance to zero.",
    )
    parser.add_argument(
        "-w", "--tile_width", type=int, help="Tile width, in pixels.", required=True
    )
    parser.add_argument(
        "-h", "--tile_height", type=int, help="Tile height, in pixels.", required=True
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        help="Output file, should include the extension, any of the formats understood by scikit-image.",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=["brute", "kriging"],
        help="Type of computation of the tile, either brute force (distance computed for each pixel) or ordinary Kriging interpolation. If not specified, brute-force is used for tiles up to 128x128 pixels.",
        default="auto",
    )
    parser.add_argument(
        "-s",
        "--samples",
        type=float,
        help="Sample points for interpolation, an integer is used as an absolute number, a floating point between 0 and 1 it is used as a percentage (default: 1%).",
        default=0.01,
    )
    parser.add_argument("wnlat", type=float, help="West North GPS latitude.")
    parser.add_argument("wnlon", type=float, help="West North GPS longitude.")
    parser.add_argument("eslat", type=float, help="East South GPS latitude.")
    parser.add_argument("eslon", type=float, help="East South GPS longitude.")
    args = parser.parse_args()
    mapdata = load_map(args)
    image = data.create_image(args.tile_width, args.tile_height)
    tile.plot(
        image,
        mapdata,
        args.type,
        (args.wnlon, args.wnlat),
        (args.eslon, args.eslat),
        verbose=args.verbose,
        points=args.samples,
    )
    data.plot_roads(
        image,
        mapdata,
        (args.wnlon, args.wnlat),
        (args.eslon, args.eslat),
        road_value=0.0 if args.zero_roads else 1.0,
    )
    data.save_image(image, args.output_file)


def one_coord():
    parser = argparse.ArgumentParser(
        description="Compute the distance-to-closest-road for a given GPS coordinate."
    )
    add_base_args(parser)
    parser.add_argument("lat", type=float, help="GPS latitude")
    parser.add_argument("lon", type=float, help="GPS longitude")

    args = parser.parse_args()
    mapdata = load_map(args)
    print(point.distance(mapdata, (args.lon, args.lat)))


def list_layers():
    parser = argparse.ArgumentParser(description="List layers in shape file.")
    add_base_args(parser)
    args = parser.parse_args()
    layers = data.list_layers(args.map)
    print("Num.\tLayer\tSize")
    for idx, layer, size in layers:
        print(f"{idx}\t{layer}\t{size}")
