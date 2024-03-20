import math

class LinearTransInfo:

    def __init__(self, offX, offY, scaleX, scaleY):
        self.offX = offX
        self.offY = offY
        self.scaleX = scaleX
        self.scaleY = scaleY


class CoordTrans:

    @staticmethod
    def robotToSlam(robotPos, x, y):
        b0 = robotPos.bearing
        c, s = math.cos(b0), math.sin(b0)
        return robotPos.x + x * c - y * s, robotPos.y + x * s + y * c

    @staticmethod
    def slamToRobot(robotPos, x, y):

        b0 = robotPos.bearing
        c, s = math.cos(-b0), math.sin(-b0)
        return robotPos.x + x * c - y * s, robotPos.y + x * s + y * c

    @staticmethod
    def slamToLocal(self, x, y):

        return (x + self.paintOffsetX) // self.MAP_SCALE, (y + self.paintOffsetY) // self.MAP_SCALE

    def localToSlam(self, x, y):

        return x * self.MAP_SCALE - self.paintOffsetX, y * self.MAP_SCALE - self.paintOffsetY

    def robotToLocal(self, robotPos, x, y):

        return self.slamToLocal(*self.robotToSlam(robotPos, x, y))

    def localToRobot(self, robotPos, x, y):

        return self.slamToRobot(robotPos, *self.localToSlam(x, y))

    def slamToGraph(self, x, y):

        return x + self.paintOffsetX, y + self.paintOffsetY

    def graphToSlam(self, x, y):

        return x - self.paintOffsetX, y - self.paintOffsetY