from model1 import Experiment
import numpy as np
import math
import random

def gen_data1(experiment):
    maxNlons = 60
    nlatsHem = maxNlons * 2
    ts_num = 3
    ilevs = 10
    distLats = 89/nlatsHem
    lats = [n*distLats for n in range (-nlatsHem, nlatsHem+1)]
    nlons = [int(maxNlons - math.trunc(abs(lat / distLats)) / 3) for lat in lats]
    nIndex = [0]
    for i in range (1, len(nlons)):
        nIndex.append(nIndex [i-1] + nlons[i])

    totalCoord = nIndex[len(nIndex)-1] + nlons[len(nlons)-1]


    for ilat, lat in enumerate(lats):
        experiment.grid[lat] = [nlons[ilat], nIndex[ilat]]

    for ts in range (ts_num):
        print("Generating data for t=%d" % ts)
        dFields = np.empty((totalCoord, ilevs))
        for icoord in range (totalCoord):
            for ilev in range (ilevs):
                dFields[icoord, ilev] = random.uniform(1, 50)
        experiment.Data.data[ts] = np.copy(dFields)
        res = np.copy(dFields)

    experiment.Data.nilev = ilevs
    experiment.nlats = nlatsHem *2+1
    experiment.nlons = maxNlons


if __name__ == '__main__':

    experiment = Experiment("my_app.experiment")
    gen_data1(experiment)
