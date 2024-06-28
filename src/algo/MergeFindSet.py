

class MergeFindSet:

    def __init__(self):
        self.father = dict()
        self.count = dict()
        self.statOK = False

    def find(self, x):

        f = self.father.get(x, x)
        return f if f == x else self.find(f)

    def merge(self, x, y):

        xf = self.find(x)
        yf = self.find(y)
        if xf != yf:
            self.father[xf] = yf

    def inSameSet(self, x, y):

        return self.find(x) == self.find(y)

    def stat(self):

        count = self.count
        count.clear()
        for k, v in self.father.items():
            f = self.find(v)
            count.setdefault(f, 0)
            count[f] += 1

        self.statOK = True


    def sizeOfSet(self, x):

        if not self.statOK:
            self.stat()

        f = self.find(x)
        return self.count[f]

