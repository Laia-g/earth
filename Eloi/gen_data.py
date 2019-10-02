import random

from hecuba import StorageDict


def gen_data(data):
    nlons = 20
    nlats = nlons * 4
    ts_num = 24 * 3
    ilevs = 137

    for ts in range(0, ts_num, 4):
        for ilev in range(0, ilevs, 10):
            for lon in range(0, nlons):
                for lat in range(0, nlats + 1):
                    klon = 360.0 * lon / nlons
                    klat = 90.0 * lat / nlats
                    data[klat, klon, ts, ilev] = [random.uniform(0, 50), random.uniform(-10, 10),
                                                  random.uniform(-50, 50)]
                    data[-klat, klon, ts, ilev] = [random.uniform(0, 50), random.uniform(-10, 10),
                                                   random.uniform(-50, 50)]


class Data(StorageDict):
    '''
    @TypeSpec dict<<lat:double, lon:double, time:double, ilev:int>, data1:double, data2:double, data3:double>
    '''


if __name__ == "__main__":
    data = Data("my_app.earth_data")
    gen_data(data)
