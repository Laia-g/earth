from model1 import Experiment1
import numpy as np
import math
import random

def gen_data1(experiment):
    maxNlons = 20
    nlatsHem = maxNlons * 2
    ts_num = 20
    ilevs = 50
    distLats = 89/nlatsHem
    lats = [n*distLats for n in range (-nlatsHem, nlatsHem+1)]
    nlons = [int(maxNlons - math.trunc(abs(lat / distLats)) / 3) for lat in lats]
    nIndex = [0]
    for i in range (1, len(nlons)):
        nIndex.append(nIndex [i-1] + nlons[i])

    totalCoord = nIndex[len(nIndex)-1] + nlons[len(nlons)-1]
    dataFields = np.empty((totalCoord, ilevs))

    for ilat, lat in enumerate(lats):
        experiment.grid[lat] = [nlons[ilat], nIndex[ilat]]

    for ts in range (ts_num):
        for icoord in range (totalCoord):
                for ilev in range (ilevs):
                    dataFields[icoord, ilev] = random.uniform(0, 50)
        experiment.Data.data[ts] = dataFields

                # for lon in range (0, nlons):
                #      for ilev in range (ilevs):
                #         for nfield in range (nfields):
                #             dataFields[ilat, ilev, nfield] = random.uniform(0, 50)


        #experiment.Data.data[ts] = dataFields

    experiment.Data.nilevs = ilevs
    experiment.nlats = nlatsHem *2+1
    experiment.nlons = maxNlons


if __name__ == '__main__':

    experiment = Experiment("myapp.experiment1")
    gen_data1(experiment)
