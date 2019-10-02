import time
from collections import defaultdict

from pycompss.api.api import compss_barrier
from pycompss.api.task import task
from hecuba import config
from gen_data import Data, gen_data


@task()
def interpolate(data, normal_data, number_points, dist):
    all_time_lats = defaultdict(list)
    for (lat, _, ts, ilev) in data.keys():
        all_time_lats[ts, ilev].append(lat)

    for (ts, ilev), lats in all_time_lats.items():
        ts_data = list(filter(lambda x: x.time == ts and x.ilev == ilev, data))
        for lat in lats:
            lat_data = list(filter(lambda x: x.key.lat == lat, ts_data))
            new_lon = 0.0
            following_point = 1
            for _ in range(number_points):
                while lat_data[following_point].key.lon < new_lon:
                    following_point += 1
                previous_point = following_point - 1

                distance_1 = new_lon - lat_data[previous_point].key.lon
                distance_2 = lat_data[following_point].key.lon - new_lon
                new_point = []
                # iterate over all the values to interpolate
                for i in range(0, len(lat_data[0].value)):
                    value_1 = lat_data[previous_point].value[i]
                    value_2 = lat_data[following_point].value[i]
                    new_point.append((distance_1 * value_2 + distance_2 * value_1) / (distance_1 + distance_2))

                normal_data[lat, new_lon, ts, ilev] = new_point
                new_lon += dist


if __name__ == "__main__":
    # config.session.execute("DROP TABLE IF EXISTS my_app.earth_data")
    config.session.execute("DROP TABLE IF EXISTS my_app.earth_normal_data")
    data = Data("my_app.earth_data")
    normal_data = Data("my_app.earth_normal_data")
    # gen_data(data)
    # print("Data generated\n")

    # Number of points in the normal grid
    number_points = 15
    dist = 360.0 / number_points
    starting_size = len(list(data.keys()))

    print("Starting interpolation\n")
    start = time.time()
    for partition in data.split():
        interpolate(partition, normal_data, number_points, dist)
    compss_barrier()
    end = time.time()

    final_size = len(list(normal_data.keys()))

    print("Total time: %s" % (end - start))
    print("Starting size: %s" % starting_size)
    print("Final size: %s" % final_size)
