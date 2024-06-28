import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


# 生成曲面各点 (x,y,z)
# 曲面点位置：(x=x, y=y, z=x*y)
# 曲面点法向: (y, x, 1.0)

# x = np.linspace(-0.5, 0.5, 10)
# y = np.linspace(-0.5, 0.5, 10)
# z = np.zeros((len(x), len(y)))
#
# nor = np.zeros((len(x), len(y),3))
# nor_x_min = np.float64('inf')
# nor_x_max = -1.0*np.float64('inf')
# nor_y_min = np.float64('inf')
# nor_y_max = -1.0*np.float64('inf')
#
# for i in range(len(x)):
#     for j in range(len(y)):
#         z[i][j] = x[i]*y[j]
#         nor[i][j] = (y[j], x[i], 1.0)
#         nor_x_min = np.fmin(nor_x_min, nor[i][j][0])
#         nor_x_max = np.fmax(nor_x_max, nor[i][j][0])
#
#         nor_y_min = np.fmin(nor_y_min, nor[i][j][1])
#         nor_y_max = np.fmax(nor_y_max, nor[i][j][1])
#
# # 绘制曲面
# # 曲面由多个面片组成 各面片颜色根据法向确定
# x, y = np.meshgrid(x, y)
# fig = plt.figure()
# ax = fig.add_subplot(
#     121, projection='3d')
# ax2 = fig.add_subplot(122, projection='3d')
#
# f = np.zeros((len(z), len(z[0])), tuple)
# for i in range(len(f)):
#     for j in range(len(f[i])):
#         f[i][j] = ((nor[i][j][0]-nor_x_min)/(nor_x_max-nor_x_min), (nor[i][j][1]-nor_y_min)/(nor_y_max-nor_y_min), 1.0)
# # 使用面片法向作为面片颜色
# ax.plot_surface(x, y, z, facecolors=f)
#
# for i in range(len(z)):
#     x[i] += 0.5
#     z[i] += 5
# ax.plot_surface(x, y, z, facecolors=f)
# ax2.plot_surface(x, y, z, facecolors=f)
#
# # 使用默认jet类型colormap作为面片颜色
# # ax.plot_surface(x, y, z, cmap=cm.jet)
# plt.show()

def getLinePart(s, index):
    parts = s.split(" ")
    return parts[index]

def getLinePart2(s, index1, index2):
    parts = s.split(" ")
    return parts[index1], parts[index2]

def getLinePart3(s, index1, index2, index3):
    parts = s.split(" ")
    return parts[index1], parts[index2], parts[index3]

class RoundData:

    def __init__(self):
        self.dist = -1
        self.diff = [0.0 for i in range(360)]

    def add(self, s, offset = 0):
        degIdxStr, difStr, avgStr = getLinePart3(s, 6 + offset, 10 + offset, 11 + offset)
        degIdx = int(degIdxStr[1:-1])
        dif = float(difStr[4:-1])
        self.diff[degIdx] = dif
        if (self.dist < 0):
            self.dist = float(avgStr[4:-2])


class LdsShake:

    def __init__(self, filePath):
        self.data = []
        self.filePath = filePath

    def drawImage(self, dataList):

        x = np.linspace(0, 60, 61, dtype=int)
        # x = np.concatenate([np.linspace(300, 359, 60, dtype=int), np.linspace(0, 60, 61, dtype=int)])
        y = np.zeros(len(dataList), dtype=float)
        z = np.zeros((len(x), len(y)), dtype=float)
        for i in range(len(dataList)):
            y[i] = dataList[i].dist
            for j in x:
                z[j][i] = min(15, dataList[i].diff[j])

        x, y = np.meshgrid(y, x)
        fig = plt.figure(dpi=300)
        ax = fig.add_subplot(
            111, projection='3d')
        # ax2 = fig.add_subplot(122, projection='3d')
        #
        f = np.zeros((len(z), len(z[0])), tuple)
        for i in range(len(f)):
            for j in range(len(f[i])):
                f[i][j] = (0.5, 0.5, 1.0)
        # 使用面片法向作为面片颜色
        ax.plot_surface(x, y, z, cmap=plt.get_cmap('rainbow'))
        ax.set_ylabel('degree')
        ax.set_xlabel('distance to front(mm)')
        ax.set_zlabel('maxdif')


        plt.show()

        print(x.shape)
        print(y.shape)
        print(z.shape)

        print("draw {}".format(len(dataList)))
        xxx = input()

    def work(self, offset):
        with open(self.filePath, "r") as file:
            for line in file:
                # if "StateLDSAndStructLightComparationTest::TestLDS" in line:
                #     print("read testLDS")
                #     token = getLinePart(line, 5)
                #     if token == "Start":
                #         print("read start")
                #         self.data.append([])
                #     elif token == "End":
                #         print("read end")
                #         self.drawImage(self.data[-1])

                if "Test: Round" in line:
                    if "1-1" == getLinePart(line, 8 + offset):
                        self.data.append([])

                    self.data[-1].append(RoundData())

                elif "StateLDSAndStructLightComparationTest::StatAndLog" in line:
                    if "LDS" == getLinePart(line, 5 + offset):
                        self.data[-1][-1].add(line, offset)

                elif "Degree LdsFilterFlag" in line:
                    self.drawImage(self.data[-1])


if __name__ == "__main__":

    ldsShake = LdsShake(sys.argv[1])
    # ldsShake = LdsShake('/Users/guanxin/errlog/LDS对比测试数据分析/UltronSC/20240119/LDS-囚牛2# 抖动测试/R0875D35100047/反光纸/000009.20240117111928663_R0875D35100047_2024011722DEV/NAV_normal_m.log')
    ldsShake.work(1)

