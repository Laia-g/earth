from hecuba import StorageDict
from model1 import ModelData, Experiment
import numpy as np
import math, time

class Distances(StorageDict):
    '''
    @TypeSpec dict <<lat:double>, dist1:numpy.ndarray, original_dist:double, previousPoint: numpy.ndarray>
    '''
    pass

def findDistances (experiment, distances):
    maxLonPoints = experiment.nlons

    for lat in experiment.grid.keys():
        nLons = experiment.grid[lat].nlons
        originalDistance = 360/nLons

        previousPoints = [math.trunc(i*nLons/maxLonPoints) for i in range(maxLonPoints)]
        dist1 =np.array( [i*originalDistance - originalDistance *previousPoints[i] %360 for i in range (nLons)])
        distances[lat] = [dist1, originalDistance, np.array(previousPoints)]


def interpolation (experiment, distances):
    for ts in experiment.Data.data.keys():
        field_values = experiment.Data.data[ts]
        for lat in experiment.grid.keys():
            i = 1
            previous = distances[lat].previousPoint
            values1 = [field_values[experiment.grid[lat].total_index + i, : ] for i in previous]
            values2 = [field_values [experiment.grid[lat].total_index + (i+1)%math.trunc(360/distances[lat].original_dist),  :] for i in previous]







if __name__ == "__main__":
    # config.session.execute("DROP TABLE IF EXISTS my_app.earth_data")
    #config.session.execute("DROP TABLE IF EXISTS my_app.earth_normal_data")

    #Data = ModelData("myapp.data")
    experiment = Experiment ("myapp.experiment1")
    distances = Distances("myapp.dist")


    start = time.time()
    print("Computing distances \n")
    findDistances(experiment, distances)
    end = time.time()
    print("Time distances: %s" % (end - start))
    start = time.time()

    print("Starting interpolation\n")
    interpolation (experiment, distances)
    end = time.time()
    print("Interpolation time: %s" % (end - start))
