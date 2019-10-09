from netCDF4 import Dataset
import os
def write (interpolated, lats, lons, ilevs, ts):
    dsout = Dataset("output.nc", "w", format="NETCDF4_CLASSIC")


    lat = dsout.createDimension ("lat", len(lats))
    lon = dsout.createDimension("lon", len(lons))
    level = dsout.createDimension ("level", len(ilevs))
    time = dsout.createDimension("time", len(ts))

    times = dsout.createVariable("time","f8",("time",))
    levels = dsout.createVariable("level","i4",("level",))
    latitudes = dsout.createVariable("lat","f4",("lat",))
    longitudes = dsout.createVariable("lon","f4",("lon",))

    latitudes [:] = lats
    longitudes [:] = lons
    times [:] = ts
    levels [:] = ilevs

    latitudes.units = "degrees north"
    longitudes.units = "degrees east"

    temp = dsout.createVariable("temp","f4",("time","level","lat","lon",))

    for t in range(len(ts)):
        temp[t, :, ::] = interpolated[t]
    dsout.close()
    print("successful writting\n")