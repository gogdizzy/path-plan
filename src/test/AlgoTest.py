from src.algo import GraphicAlgo, HullType, MergeFindSet
from src.geometry import Point2D, distanceSquare


def ClusterPoints(points, dist):

    distSqr = dist * dist
    mfs = MergeFindSet()

    for i in range(0, len(points)):
        for j in range(i + 1, len(points)):
            if distanceSquare(points[i], points[j]) <= distSqr:
                mfs.merge(i, j)

    res = dict()
    for i in range(0, len(points)):
        group = mfs.find(i)
        res.setdefault(group, []).append(points[i])

    print(res)

    return res.values()

pts = [(-60, -78),  (-50, -77),  (-61, -229),  (-52, -228),  (-44, -207),  (-36, -186),  (-40, -256),  (-31, -225),  (-20, -234),  (104, 223),  (99, 235),  (71, 221),  (-97, 58)]
pts2 = []
for p1 in pts:
    pts2.append(Point2D(p1[0], p1[1]))

print(pts2)

groups = ClusterPoints(pts2, 50)
for group in ClusterPoints(pts2, 50):
    print(group)


# for x in range(0,  6):
#     for y in range(3,  6):
#         pts.append(Point2D(x,  y))
# 
# for x in range(0,  2):
#     for y in range(0,  3):
#         pts.append(Point2D(x,  y))
# 
# for x in range(4,  6):
#     for y in range(0,  3):
#         pts.append(Point2D(x,  y))
# 
# hull = GraphicAlgo.getHull(pts,  HullType.ConcaveHull_KNN)
# 
# for p in hull:
#     print("hull vertex: {} {}".format(p.x,  p.y))
