from src.utils import GridMapPPM, GridType

fileName = '/Users/guanxin/errlog/lowobs/test/20240917/000613.20240913211957726_R17TFD41900068_2024091333REL_1/navmap20978648.ppm'

file = GridMapPPM()

file.loadData(fileName, False)

mapData = file.mapData

pairTot = 0
changeTot = 0
for y in range(file.mapHeight):
    pairCnt = 0
    changeCnt = 0
    for x in range(1, file.mapWidth):
        if mapData[x][y] == GridType.Obstacle and mapData[x-1][y] != GridType.Obstacle:
            pairCnt += 1
        if mapData[x][y] != mapData[x-1][y]:
            changeCnt += 1

    print("{}: {} {}".format(y, pairCnt, changeCnt))
    pairTot += pairCnt
    changeTot += changeCnt

print("pairTot: {}  changeTot: {}".format(pairTot, changeTot))


