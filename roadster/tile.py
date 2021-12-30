import time
import random
import multiprocessing

import roadster.data as data
import roadster.point as point

import numpy as np
import shapely.geometry as sg
import pykrige.kriging_tools as kt
from pykrige.ok import OrdinaryKriging

_mapdata = None


def _set_mapdata(data):
    global _mapdata
    _mapdata = data


def _one_distance(task):
    global _mapdata

    sample, px, py = task
    return sample, px, py, point.distance(_mapdata, (px, py))


def plot(
    image: np.ndarray,
    mapdata: list,
    inter_type: str,
    ul: tuple,
    lb: tuple,
    verbose=False,
    points=None,
    boost=1000.0,
    seed=42,
):
    """Plot the feature in a given tile."""

    h, w = image.shape

    if not points:
        points = int(h * w * 0.01)
    elif points < 1:
        points = int(h * w * points)
    else:
        points = int(points)

    rnd = random.Random(seed)

    ul_p = sg.Point(*ul)
    lb_p = sg.Point(*lb)

    gps_w = lb[0] - ul[0]
    gps_h = lb[1] - ul[1]

    w_dot = gps_w / w
    h_dot = gps_h / h

    good = data.pre_filter(mapdata, ul, lb)
    if verbose:
        print("Roads around tile: {:,}".format(len(good)))

    if not good:
        if verbose:
            print("No roads nearby, bailing out.")
        return image

    def coord2px(c):
        x = (c[0] - ul[0]) * 1.0 / w_dot
        y = (c[1] - ul[1]) * 1.0 / h_dot

        x, y = y, x

        return (max(0, min(int(x), w - 1)), max(0, min(int(y), h - 1)))

    if inter_type == "kriging" or (inter_type == "auto" and h * w > 128 * 128):
        if verbose:
            print("Doing ordinary kriging")
        kdata = np.zeros((points, 3), dtype=float)

        if False:
            started = time.time()
            for sample in range(points):
                c0 = rnd.random()
                c1 = rnd.random()
                px = ul[0] + c0 * gps_w
                py = ul[1] + c1 * gps_h
                point = sg.Point(px, py)
                kdata[sample] = [px, py, min([point.distance(obj) for obj in good])]

                if verbose and (sample + 1) % 1000 == 0:
                    print(
                        "Sampled: {:,} ({}%) in {:,} secs".format(
                            sample + 1,
                            (sample + 1) / points * 100.0,
                            time.time() - started,
                        )
                    )
                    print(np.histogram(kdata[:sample, 2])[1])
        else:
            tasks = list()
            started = time.time()
            for sample in range(points):
                c0 = rnd.random()
                c1 = rnd.random()
                px = ul[0] + c0 * gps_w
                py = ul[1] + c1 * gps_h
                tasks.append((sample, px, py))

            with multiprocessing.Pool(
                initializer=_set_mapdata, initargs=[good]
            ) as pool:
                completed = 0
                for sample, px, py, dist in pool.imap_unordered(_one_distance, tasks):
                    kdata[sample] = [px, py, dist]
                    completed += 1
                    if verbose and (completed + 1) % 1000 == 0:
                        print(
                            "Sampled: {:,} ({}%) in {:,} secs".format(
                                completed + 1,
                                (completed + 1) / points * 100.0,
                                time.time() - started,
                            )
                        )
                        print(np.histogram(kdata[:, 2])[1])
        if verbose:
            print(
                "Sampling {:,} points took {:,} secs".format(
                    points, time.time() - started
                )
            )
            print("lat", np.histogram(kdata[:, 0])[1])
            print("lng", np.histogram(kdata[:, 1])[1])

        started = time.time()
        OK = OrdinaryKriging(
            kdata[:, 0],
            kdata[:, 1],
            kdata[:, 2],
            variogram_model="gaussian",
            coordinates_type="geographic",
            nlags=20,
            verbose=verbose,
            enable_plotting=False,
        )
        if verbose:
            print("Kriging model took {:,} secs".format(time.time() - started))

        started = time.time()

        gridx = np.arange(ul[0], lb[0], w_dot)
        gridy = np.arange(ul[1], lb[1], h_dot)

        z, ss = OK.execute("grid", gridx, gridy, backend="C", n_closest_points=100)
        if verbose:
            print(np.histogram(z))
            print(
                "Executing Kriging model took {:,} secs".format(time.time() - started)
            )

        image[:, :] = z
    else:
        if verbose:
            print("Doing brute-force")
        started = time.time()
        completed = 0
        for x in range(w):
            for y in range(h):
                point = sg.Point(ul[0] + x * w_dot, ul[1] + y * h_dot)
                image[y, x] = min([point.distance(obj) for obj in good])
                completed += 1
                if verbose and completed % 1000 == 0:
                    print(
                        "Completed: {:,} ({}%) in {:,} secs".format(
                            completed, completed / (h * w) * 100, time.time() - started
                        )
                    )

    data.boost(image, level=boost)
