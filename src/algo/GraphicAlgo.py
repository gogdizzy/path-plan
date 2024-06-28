import math
from collections import deque
from enum import IntEnum

import cv2
import numpy as np
import scipy.interpolate as si
from PyQt5.QtCore import QPoint

from src.geometry import crossProduct


class HullType(IntEnum):

    ConvexHull_GrahamScan = 1
    ConcaveHull_KNN = 2

class GraphicAlgo:

    @staticmethod
    def bspline(cv, n=100, degree=3, periodic=False):
        """ Calculate n samples on a bspline

            cv :      Array ov control vertices
            n  :      Number of samples to return
            degree:   Curve degree
            periodic: True - Curve is closed
                      False - Curve is open
        """

        # If periodic, extend the point array by count+degree+1
        cv = np.asarray(cv)
        count = len(cv)

        if periodic:
            factor, fraction = divmod(count + degree + 1, count)
            cv = np.concatenate((cv,) * factor + (cv[:fraction],))
            count = len(cv)
            degree = np.clip(degree, 1, degree)

        # If opened, prevent degree from exceeding count-1
        else:
            degree = np.clip(degree, 1, count - 1)

        # Calculate knot vector
        kv = None
        if periodic:
            kv = np.arange(0 - degree, count + degree + degree - 1, dtype='int')
        else:
            kv = np.concatenate(([0] * degree, np.arange(count - degree + 1), [count - degree] * degree))

        # Calculate query range
        u = np.linspace(periodic, (count - degree), n)

        # Calculate result
        return np.array(si.splev(u, (kv, cv.T, degree))).T

    @staticmethod
    def cornerHarris(img, blocksize=2, ksize=3, k=0.04):
        def _clacHarris(cov, k):
            result = np.zeros([cov.shape[0], cov.shape[1]], dtype=np.float32)
            for i in range(cov.shape[0]):
                for j in range(cov.shape[1]):
                    a = cov[i, j, 0]
                    b = cov[i, j, 1]
                    c = cov[i, j, 2]
                    result[i, j] = a * c - b * b - k * (a + c) * (a + c)
            return result

        Dx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=ksize)
        Dy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=ksize)

        cov = np.zeros([img.shape[0], img.shape[1], 3], dtype=np.float32)

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                cov[i, j, 0] = Dx[i, j] * Dx[i, j]
                cov[i, j, 1] = Dx[i, j] * Dy[i, j]
                cov[i, j, 2] = Dy[i, j] * Dy[i, j]
        cov = cv2.boxFilter(cov, -1, (blocksize, blocksize), normalize=False)
        return _clacHarris(cov, k)

    @staticmethod
    def getBresenhamPoints8(ptBeg, ptEnd):
        ret = []

        x0, y0, x1, y1 = ptBeg.x(), ptBeg.y(), ptEnd.x(), ptEnd.y()
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        steep = dy > dx
        if steep:
            x0, y0, x1, y1 = y0, x0, y1, x1
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0

        dx, dy = abs(x1 - x0), abs(y1 - y0)
        err = dx // 2
        stepY = 1 if y0 <= y1 else -1
        x, y = x0, y0
        while True:
            ret.append(QPoint(y, x) if steep else QPoint(x, y))
            if x == x1 and y == y1:
                break
            err -= dy
            if err < 0:
                y += stepY
                err += dx
            x += 1

        return ret

    @staticmethod
    def getBresenhamPoints4(ptBeg, ptEnd):
        ret = []

        x0, y0, x1, y1 = ptBeg.x(), ptBeg.y(), ptEnd.x(), ptEnd.y()
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x1 > x0 else -1
        sy = 1 if y1 > y0 else -1

        err = 0
        x, y = x0, y0
        for i in range(0, dx + dy + 1):
            ret.append(QPoint(x, y))
            ex = err + dy
            ey = err - dx
            if abs(ex) < abs(ey):
                x += sx
                err = ex
            else:
                y += sy
                err = ey

        return ret


    @staticmethod
    def getHull(points, type, param=None):

        if type == HullType.ConvexHull_GrahamScan:
            return GraphicAlgo.GrahamScan(points)

        elif type == HullType.ConcaveHull_KNN:
            return GraphicAlgo.ConcaveHullKNN(points, param)

    @staticmethod
    def GrahamScan(points):
        def is_left(p0, p1, p2):
            return crossProduct(p1 - p0, p2 - p0) >= 0

        def sort_by_angle(points, p0):
            def angle(p1):

                dx = p1.x - p0.x
                dy = p1.y - p0.y
                return math.atan2(dy, dx)

            return sorted(points, key=angle)

        # Find the point with the smallest y coordinate.
        p0 = min(points, key=lambda p: p.y)

        points = sort_by_angle(points, p0)

        stack = deque([p0, points[0], points[1]])

        for p in points[2:]:
            while len(stack) >= 2 and not is_left(stack[-2], stack[-1], p):
                stack.pop()
            stack.append(p)

        return stack

    @staticmethod
    def ConcaveHullKNN(points, k):

        dataset = set(points)
        pointCnt = len(dataset)

        if pointCnt < 3:
            return None
        if pointCnt == 3:
            return list(dataset)

        kk = min(max(k, 3), pointCnt - 1)
        # Find the point with the smallest y coordinate.
        firstPoint = min(points, key=lambda p: p.y)
        hull = [firstPoint]
        currentPoint = firstPoint
        dataset.remove(firstPoint)
        prevAngle = math.pi
        step = 2

        def FindNearestPoints(pts, p0, n):

            def DistanceAndAngle(p):

                def GetAngle(p):

                    angle = math.atan2(p.y - p0.y, p.x - p0.x)
                    while angle > prevAngle:
                        angle -= 2 * math.pi
                    while angle < prevAngle - 2 * math.pi:
                        angle += 2 * math.pi

                    return angle

                distSqr = (p.x - p0.x) * (p.x - p0.x) + (p.y - p0.y) * (p.y - p0.y)

                return distSqr * 100 + GetAngle(p)

            pts2 = list(pts)
            pts2 = sorted(pts2, key=DistanceAndAngle)
            if len(pts2) >= n:
                return pts2[0:n]
            else:
                return pts2

        def SortByAngle(pts, p0, preAngle):

            def GetAngle(p):

                angle = math.atan2(p.y - p0.y, p.x - p0.x)
                while angle > preAngle:
                    angle -= 2 * math.pi
                while angle < preAngle - 2 * math.pi:
                    angle += 2 * math.pi

                return angle

            return sorted(pts, key=GetAngle)

        def JudgeIntersect(pts):

            def SegIntersect(p1, p2, p3, p4):

                if max(p1.x, p2.x) < min(p3.x, p4.x) or \
                   max(p1.y, p2.y) < min(p3.y, p4.y) or \
                   max(p3.x, p4.x) < min(p1.x, p2.x) or \
                   max(p3.y, p4.y) < min(p1.y, p2.y):
                    return False

                if crossProduct(p1 - p3, p4 - p3) * crossProduct(p2 - p3, p4 - p3) > 0 or \
                   crossProduct(p3 - p1, p2 - p1) * crossProduct(p4 - p1, p2 - p1) > 0:
                    return False

                return True

            for p in pts:
                st = 0
                if p == firstPoint:
                    st = 1
                its = False
                for j in range(st, len(hull) - 2):
                    if SegIntersect(p, hull[-1], hull[j], hull[j+1]):
                        its = True
                        break
                if not its:
                    return False, p

            return True, None

        while (currentPoint != firstPoint or step == 2) and len(dataset) > 0:
            if step == 5:
                dataset.add(firstPoint)

            nearestPoints = FindNearestPoints(dataset, currentPoint, kk)
            cPoints = SortByAngle(nearestPoints, currentPoint, prevAngle)
            allIntersect, newPoint = JudgeIntersect(cPoints)
            if allIntersect:
                return GraphicAlgo.ConcaveHullKNN(points, k + 1)

            currentPoint = newPoint
            if currentPoint != firstPoint:
                hull.append(currentPoint)
            prevAngle = math.atan2(hull[-2].y - hull[-1].y, hull[-2].x - hull[-1].x)
            dataset.remove(currentPoint)
            step += 1

        def IsInPolygon(pt, pts):

            # for i in range(-1, len(pts) - 1):
            #     if crossProduct(pts[i+1] - pts[i], pt - pts[i]) < 0:
            #         return False
            return True

        for p in dataset:
            if not IsInPolygon(p, hull):
                return GraphicAlgo.ConcaveHullKNN(points, k + 1)

        return hull
