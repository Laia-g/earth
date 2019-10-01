from hecuba import StorageDict
from model1 import ModelData, Experiment
import numpy as np
import math, time

class Distances(StorageDict):
    '''
    @TypeSpec dict <<lat:double>, dist1:numpy.ndarray, original_dist:double, previousPoint: numpy.ndarray>
    '''
    pass
class interpolatedData (StorageDict):
    '''
    @TypeSpec dict <<ts:double>, fields_data:numpy.ndarray>
    '''

def findDistances (experiment, distances):
    maxLonPoints = experiment.nlons
    newDistance = 360/maxLonPoints
    for lat in experiment.grid.keys():
        nLons = experiment.grid[lat].nlons
        originalDistance = 360/nLons

        previousPoints = [math.trunc(i*nLons/maxLonPoints) for i in range(maxLonPoints)]
        dist1 =np.array( [i*newDistance - originalDistance *previousPoints[i] for i in range (maxLonPoints)])
        distances[lat] = [dist1, originalDistance, np.array(previousPoints)]


def interpolation (experiment, distances):
    interpolated = interpolatedData("myapp.interpolated")
    interpolatedFields = np.empty((experiment.nlats, experiment.nlons, experiment.Data.nilev))
    for ts in experiment.Data.data.keys():
        field_values = experiment.Data.data[ts]
        for ilat,lat in enumerate(experiment.grid.keys()):
            originalDistance = distances[lat].original_dist
            previous = distances[lat].previousPoint
            values1 = np.array([field_values[experiment.grid[lat].total_index + i, : ] for i in previous])
            following = previous +1
            following [ following == experiment.grid[lat].nlons] = 0
            values2 = np.array([field_values [experiment.grid[lat].total_index + (i),  :] for i in following])
            distances1 = distances[lat].dist1
            distances2 = originalDistance - distances1
            interpolatedFields [ilat, :, : ] = (np.multiply(values1, distances1[:, None]) + np.multiply(values2, distances2[:, None]))/originalDistance
        interpolated[ts] = interpolatedFields;






if __name__ == "__main__":
    # config.session.execute("DROP TABLE IF EXISTS my_app.earth_data")
    #config.session.execute("DROP TABLE IF EXISTS my_app.earth_normal_data")

    #Data = ModelData("myapp.data")
    experiment = Experiment ("my_app.experiment")
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
