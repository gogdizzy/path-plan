import math

def degToRad(deg):
    return deg / 180.0 * math.pi


def radToDeg(rad):
    return rad / math.pi * 180.0


def clipAngle(rad):
    while rad >= math.pi:
        rad -= math.pi * 2
    while rad < -math.pi:
        rad += math.pi * 2

    return rad


def clipValue(v, minv, maxv):
    if v < minv:
        return minv
    if v > maxv:
        return maxv
    return v