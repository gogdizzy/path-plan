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


def clipDegree(deg):
    while deg >= 180:
        deg -= 360
    while deg < -180:
        deg += 360

    return deg


def clipValue(v, minv, maxv):
    if v < minv:
        return minv
    if v > maxv:
        return maxv
    return v

def crossProduct(p1, p2):
    return p1.x * p2.y - p1.y * p2.x

def distanceSquare(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return dx * dx + dy * dy

