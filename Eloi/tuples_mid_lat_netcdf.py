from classes_tuples import GridPoints, GlobalStats
from pycompss.api.task import task
from pycompss.api.api import compss_barrier, compss_wait_on
from pycompss.api.parameter import *
import time

def compute_stats(m, v):
    return m._replace(sum=m.sum+v, min=min(m.min, v), max=max(m.max, v), count=m.count+1)

@task(returns=1)
def pre_interpolate(partition, NP, dist):
    keyDict = {}
    tl = set()
    for r in partition.iterkeys():
        tl.add(r.time)
        if r.lat not in keyDict:
            keyDict[r.lat] = []
        else:
            keyDict[r.lat].append(r.lon)
    indexes = {}
    for lat in keyDict.keys():
        indexes[lat] = []
        n_lat = len(keyDict[lat])
        new_lon = 0.0
        i = 0
        for _ in range(NP):
            while i < n_lat and keyDict[lat][i] <= new_lon:
                i += 1
            indexes[lat].append(i)
            new_lon += dist
    return keyDict, list(tl), indexes

@task(d=CONCURRENT)
def interpolate_lat(d, partition, NP, dist, lat, keyList, tl, idxList):
    num_t = 4 * 4 * 6 # Input each 15 minutes (i.e. 0 is minute 0, 4 is minute 60, 8 is minute 120, 96 is minute 1440 and thats the next day already)
    localStats = GlobalStats()

    auxd = {}
    latlen = len(keyList)
    for t in tl:
        index = t / num_t
        new_lon = 0.0
        for p2i in idxList:
            # Avoids wrong index access
            if p2i == latlen:
                p2i = -1
            p1i = p2i - 1
            d1 = new_lon - keyList[p1i]
            d2 = keyList[p2i] - new_lon
            range_n = 8
            try:
                auxd[lat, keyList[p1i], t]
            except KeyError:
                auxd[lat, keyList[p1i], t] = partition[lat, keyList[p1i], t]
            try:
                auxd[lat, keyList[p2i], t]
            except KeyError:
                auxd[lat, keyList[p2i], t] = partition[lat, keyList[p2i], t]
            for ilev, row in enumerate(auxd[lat, keyList[p2i], t]):
                stats = localStats[index, lat, new_lon, ilev]
                for i in range(range_n):
                    p1 = auxd[lat, keyList[p1i], t][ilev][i]
                    p2 = row[i]
                    p = (d1 * p2 + d2 * p1) / (d1 + d2)
                    stats[i] = compute_stats(stats[i], p)
                localStats[index, lat, new_lon, ilev] = stats
            new_lon += dist
    d.update(localStats)

if __name__ == "__main__":
    # Number of points in the normal grid
    NP = 1024 #2560
    dist = 360.0 / NP
    # Using same input data for each execution
    sdict = GridPoints('test.gj3g_ml')
    dayStats = GlobalStats('daytest')

    time1 = time.time()
    infoList = []

    from netCDF4 import Dataset

    #reference file
    dsin = Dataset("/gpfs/scratch/bsc31/bsc31906/Storm_Xaver/T511/output1/netcdf_means.nc", "r")

    #output file
    import os
    dsout = Dataset("output-" + os.environ["SLURM_JOBID"] + ".nc", "w", format="NETCDF4_CLASSIC")

    #Copy dimensions
    for dname, the_dim in dsin.dimensions.iteritems():
        print dname, len(the_dim)
        dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

    # Copy variables
    for v_name, varin in dsin.variables.iteritems():
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
    
        #outVar[:] = varin[:] # Not copying the content itself.

    # close the input file
    dsin.close()

    # TODO: FILLING THE OUTPUT FILE ITERATING OVER DATA IN CASSANDRA

    for partition in sdict.split():
        infoList.append(pre_interpolate(partition, NP, dist))
    infoList = compss_wait_on(infoList)
    for keyDict, tl, idxDict in infoList:
        for lat in keyDict:
            interpolate_lat(dayStats, sdict, NP, dist, lat, keyDict[lat], tl, idxDict[lat])
    compss_barrier()
    print "Execution time: " + str(time.time() - time1) + " seconds."
