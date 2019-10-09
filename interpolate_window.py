from hecuba import StorageDict
from model1 import Experiment
import numpy as np
import math, time
from testnetcdf import write
from generate1 import gen_data1
from pycompss.api.api import compss_barrier, compss_wait_on
from pycompss.api.task import task


@task(returns = dict)
def findDistances (grid, lats, maxLonPoints):
    distances = {}
    newDistance = 360/maxLonPoints
    for lat in lats:
        nLons = grid[lat].nlons
        originalDistance = 360/nLons

        previousPoints = np.array([math.trunc(i*nLons/maxLonPoints) for i in range(maxLonPoints)])
        dist1 =np.array( [i*newDistance - originalDistance *previousPoints[i] for i in range (maxLonPoints)])
        #distances[lat] = [dist1, originalDistance, np.array(previousPoints)]
        distances[lat] = [dist1, originalDistance, previousPoints]
    return distances

@task(returns = dict)
def interpolation (data, grid, distances, newNlons, nilev, lats, ind_lon1, ind_lon2):
    interpolated = {}
    interpolatedFields = np.empty((len(lats), newNlons, nilev))
    for ts in data.keys(): #Potser es podria canviar ts per lats
        field_values = data[ts]
        for ilat,lat in enumerate(lats):
            originalDistance = distances[lat][1]
            previous = distances[lat][2] [ind_lon1: ind_lon2+1]
            values1 = np.array([field_values[grid[lat].total_index + i, : ] for i in previous])
            following = previous +1
            following [ following == grid[lat].nlons] = 0
            values2 = np.array([field_values [grid[lat].total_index + (i),  :] for i in following])
            distances1 = distances[lat][0][ind_lon1: ind_lon2+1]
            distances2 = originalDistance - distances1
            interpolatedFields [ilat, :, : ] = (np.multiply(values1, distances2[:, None]) + np.multiply(values2, distances1[:, None]))/originalDistance
        interpolated[ts] = interpolatedFields
    return interpolated

def mergeReduce (data):
    while len(data):
        print("Merging, %d partitions left \n" % len(data))
        x = data.pop()
        if len(data):
            y = data.pop()
            data.append(mergeDicts(x, y))
        else:
            return x

def mergeDicts (dict1, dict2):
    result = dict1.copy()
    result.update(dict2)
    return result




if __name__ == "__main__":

    # config.session.execute("DROP TABLE IF EXISTS my_app.earth_data")
    # config.session.execute("DROP TABLE IF EXISTS my_app.earth_normal_data")

    # Data = ModelData("myapp.data")
    experiment = Experiment("exp1")
    gen_data1(experiment)
    window_lat1 = -90
    window_lat2 = 90
    window_lon1 = 0
    window_lon2 = 360
    lats = [] #I si inicio les lats de distances en comptes de crear una llista?
    newNlons = 0
    grid = experiment.grid
    nilev = experiment.Data.nilev
    for lat in grid.keys():
        if window_lat1 <=lat and window_lat2 >= lat: #Així es perd una mica de info. Hi ha algun problema?
            lats.append(lat)
            if experiment.grid[lat].nlons > newNlons:
                newNlons = experiment.grid[lat].nlons
    start = time.time()
    print("Computing distances \n")

    distances = []
    for partition in grid.split():
        distances.append(findDistances(partition, lats, newNlons))
    distances = mergeReduce (distances)
    distances = compss_wait_on(distances)

    end = time.time()
    print("Time distances: %s" % (end - start))

    distance_window = 360/newNlons
    index1 = int(window_lon1/distance_window)
    index2 = min(math.ceil(window_lon2/distance_window), newNlons-1)


    start = time.time()
    interpolated = []
    print("Starting interpolation\n")
    data = experiment.Data.data
    for i, partition in enumerate(data.split()):
        interpolated.append(interpolation(partition, grid, distances,  index2-index1+1 , nilev, lats, index1, index2))
    interpolated = mergeReduce(interpolated)
    interpolated=compss_wait_on(interpolated)

    #interpolation (data, grid, distances, interpolated, index2-index1+1 , nilev, lats, index1, index2)
    end = time.time()
    print("Interpolation time: %s" % (end - start))

    lons =[index1+distance_window*i for i in range (index2-index1+1 )]

    ilevs = [x for x in range(experiment.Data.nilev)]
    ts = [x for x in range(len(list(experiment.Data.data.keys())))]
    write(interpolated, lats, lons, ilevs, ts)
