from PyQt5.QtCore import QPoint


class GraphicAlgo:

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