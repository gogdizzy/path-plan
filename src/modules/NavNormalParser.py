from src.geometry import Point2D
from src.modules import TimeAndPoint2D, Pose2DAndValue


class NavNormalParser:

    def __init__(self, filename):

        self.filename = filename

    def getCamera2DPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "Camera2DBumper" in line and "Input data" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "data:":
                        timestamp = int(parts[0].split(",")[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    elif parts[7] == "data:":
                        timestamp = int(parts[1])
                        for i in range(8, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoint2D(timestamp, points))

        return res

    def getGotoObsPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "nearObs" in line and "GotoObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "nearObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoint2D(timestamp, points))

        return res


    def getGotoObsPointsBeforeMix(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "before mix" in line and "GotoFollowRouting" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[7] == "mix:":
                        timestamp = int(parts[1])
                        for i in range(8, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoint2D(timestamp, points))

        return res

    def getGotoObsPointsAfterMix(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "after mix" in line and "GotoFollowRouting" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[7] == "mix:":
                        timestamp = int(parts[1])
                        for i in range(8, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoint2D(timestamp, points))

        return res

    def getLowObsPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                if "nearObs" in line and "LowObsMap" in line:
                    points = []
                    parts = line.split(" ")
                    if parts[6] == "nearObs:":
                        timestamp = int(parts[1])
                        for i in range(7, len(parts) - 1):   # tail is space
                            x, y = map(int, parts[i].split(","))
                            points.append(Point2D(x, y))

                    res.append(TimeAndPoint2D(timestamp, points))

        return res

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
                    offset = 5
                    if parts[5] == "maybeOnCarpet":
                        offset = 5
                    elif parts[6] == "maybeOnCarpet":
                        offset = 6

                    avgCurrent = int(parts[offset + 2])
                    mbSpeed = int(parts[offset + 7])

                    if avgCurrent > 50 and mbSpeed == mainBrushSpeed:

                        x = int(parts[offset + 22])
                        y = int(parts[offset + 23])

                        res.append(Pose2DAndValue(x, y, avgCurrent))

        return res


    def getBin5LaserPoints(self):

        res = []

        with open(self.filename, mode="r") as file:

            for line in file:

                points = []
                parts = line.split(" ")
                if parts[6] != "":
                    timestamp = int(parts[0])
                    for i in range(6, len(parts) - 1):   # tail is space
                        x, y = map(int, parts[i].split(","))
                        points.append(Point2D(x, y))

                res.append(TimeAndPoint2D(timestamp, points))

        return res





