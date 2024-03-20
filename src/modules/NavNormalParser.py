from src.geometry import Point2D
from src.modules import TimeAndPoint2D, Pose2DAndValue


class NavNormalParser:

    def __init__(self, filename):

        self.filename = filename

    def getEasyStuckPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "EasyStuckPoint" in line and "StereoVision" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "EasyStuckPoint:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoint2D(timestamp, points))

        return res

    def getMainBrushData(self, mainBrushSpeed):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "maybeOnCarpet" in line and "CarpetDetectorByCurrent" in line:
                    parts = line.split(" ")
                    offset = 6
                    if parts[6] == "maybeOnCarpet":
                        offset = 6
                    elif parts[7] == "maybeOnCarpet":
                        offset = 7

                    avgCurrent = int(parts[offset + 2])
                    mbSpeed = int(parts[offset + 7])

                    if avgCurrent > 50 and mbSpeed == mainBrushSpeed:

                        x = int(parts[offset + 22])
                        y = int(parts[offset + 23])

                        res.append(Pose2DAndValue(x, y, avgCurrent))

        return res








