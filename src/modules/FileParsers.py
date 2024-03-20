
class NearObsParser:

    def __init__(self, filename, startTimestamp=0):

        self.timestamp = []
        self.obsData = []

        with open(filename, mode="r") as fp:

            for line in fp:
                arr = line.rstrip().split(" ")
                self.timestamp.append(int(arr[1]))
                obs = []
                for i in range(7, len(arr)):
                    x, y = map(int, arr[i].split(","))
                    obs.append((x, y))
                self.obsData.append(obs)

