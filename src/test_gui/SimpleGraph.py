import numpy as np
import matplotlib.pyplot as plt

# 生成外尖和内交叉点
theta = np.arange(0, 2*np.pi, 2*np.pi/5)
x_outer, y_outer = np.cos(theta), np.sin(theta)
x_inner = 0.382 * np.cos(theta + np.pi/5)  # 0.382≈cos(54°)/cos(18°)
y_inner = 0.382 * np.sin(theta + np.pi/5)

# 按步长2连接顶点
x_star = np.array([x_outer, x_inner]).flatten('F')  # 交替合并
y_star = np.array([y_outer, y_inner]).flatten('F')

plt.figure(figsize=(5,5))
plt.plot(x_star, y_star, 'r-', linewidth=2)
plt.axis('equal')
plt.title("Standard Five-Pointed Star")
plt.show()