import sys

from PyQt5 import Qt3DCore, Qt3DExtras, Qt3DRender
from PyQt5.QtGui import QColor, QVector3D
from PyQt5.QtWidgets import QApplication, QMainWindow


app = QApplication(sys.argv)
# 创建主窗口
window = QMainWindow()
scene = Qt3DCore.QEntity()
# 创建3D物体
torus = Qt3DExtras.QTorusMesh()
material = Qt3DExtras.QPhongMaterial()
# 设置3D物体的参数
torus.setRadius(1)
torus.setMinorRadius(0.4)
torus.setRings(100)
torus.setSlices(20)
# 设置物体的材质
material.setDiffuse(QColor("#FFD700"))
# 将物体和材质添加到场景中
torusEntity = Qt3DCore.QEntity(scene)
torusEntity.addComponent(torus)
torusEntity.addComponent(material)
# 设置摄像机
camera = Qt3DRender.QCamera(scene)
camera.lens().setPerspectiveProjection(45, 16 / 9, 0.1, 1000)
camera.setPosition(QVector3D(0, 0, 20))
camera.setViewCenter(QVector3D(0, 0, 0))
# 设置3D视图
view = Qt3DExtras.Qt3DWindow()
view.setRootEntity(scene)
# view.setCamera(camera)
view.show()
sys.exit(app.exec_())
