import math 
# This file will be primary spatial math. Give a flight trajectory(Long, Lat, Time, Alt, Groundspeed)
# The kinematic and naviagtion data is not useful for ML model. Spatial/geometric data is what we want.
# We will use Kinematic/Nav data to find:

# 1. distance between two points
def distance(lat1, lon1, lat2, lon2):
    # convert from degree to radians 
    rlat1 = math.radians(lat1)
    rlon1 = math.radians(lon1)
    rlat2 = math.radians(lat2)
    rlon2 = math.radians(lon2)
    # Angular diff, find the distance between lat pair and lon pair
    delta_lat = rlat2 - rlat1
    delta_lon = rlon2 - rlon1
    # haversine formula will find the central angle, which is the central point of the angle the two points make.
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(rlat1) * math.cos(rlat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Multiply by Earth radius
    R = 6371000
    # Return distance
    return R * c

# 2. bearing(direction of travel): north 0°, east 90°, south 180°, west 270° 
def bearing(lat1, lon1, lat2, lon2):
    # convert from degree to radians 
    rlat1 = math.radians(lat1)
    rlon1 = math.radians(lon1)
    rlat2 = math.radians(lat2)
    rlon2 = math.radians(lon2)
    # Angular diff, find the distance between lat pair and lon pair
    delta_lon = rlon2 - rlon1

    # spherical bearing formula (also called the initial bearing or forward azimuth, calculates 
    # the direction you must start moving from point 1 to reach point
    y = math.sin(delta_lon) * math.cos(rlat2)
    x = (
        math.cos(rlat1) * math.sin(rlat2)
        - math.sin(rlat1) * math.cos(rlat2) * math.cos(delta_lon)
    )
    theta = math.atan2(y, x) 
    deg = math.degrees(theta) 
    return (deg + 360) % 360  

# 3. Turn angle(change in bearing between two consecutive segments.)

# Take two bearings in degrees
# Return the smallest signed difference
# Output range should be:
# -180° to +180°
def turn_angle(bearing1, bearing2):
    return (bearing2 - bearing1 + 180) % 360 - 180