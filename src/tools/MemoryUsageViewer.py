#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MemoryUsageViewer.py
1> 是一个 gui 界面的工具，使用 pyqt5 进行开发
2> 可以提供一个 gui 选择窗口，选择一张 ppm 地图，ppm 格式可以参考 utils/GridMapPPM.py 的打开方式，或者直接调用这个类也行，不需要 trim 周围
3> 打开 ppm 地图以后，需要显示在 gui 背景上，如果超过屏幕，需要有滚动条，可以查看整个地图，记住地图的坐标系，左下角到右上角对应的是 [-512, -512] 到 [511, 511]
4> 另外提供一个按钮 AddLog，点击以后，也是打开一个选择窗口，可以选择添加日志，把日志添加进来，添加的过程中可以显示加载的进度条
5> 日志格式有几种：
    a. 1207,2614350 T3935 VisionStructLight::VisionStructLight::PrintMemoryUsage:1580 [info] [PL6] VisionObs-LOOSEWIRE map this 0x7f84c14750 range=[0 0 1023 1023] center=[0 0] use memory 0
     日志格式说明：
       这种日志可以通过关键字 PrintMemoryUsage 抽取
       第一个逗号后面是时间戳
       [PL6] 后面是地图名称，例如这个是"VisionObs-LOOSEWIRE"
       this 后面是地图的内存地址
       use memory 后面是地图使用的内存大小
     b. 1239, 2614357 T3962 ClusterGridMapX::SetAll:384 [info] [PL6] ClusterGridMapImpl::SetAll this 0x7f80e0f610 prevBlockCount: 0 to 0, maxBlockCount 128 releaseMem 0
       日志格式说明：
        这种日志可以通过关键字 ClusterGridMapX::SetAll 抽取
        第一个逗号后面是时间戳，注意这个日志和上面有区别，第一个逗号后面还有个空格
        this 后面是地图的内存地址，对于这种操作，可以认为地图被清空了
     c. 1240, 2614357 T3962 ClusterGridMapX::At:338 [info] [PL6] ClusterGridMapImpl::At NewBlock this 0x7f84c13310 x=515, y=509, blockStart(512 448) tableIdx=120, blockCount=53, maxBlockCount=128, mapRange=[0 0 1023 1023]
       日志格式说明：
        这种日志可以通过关键字 "ClusterGridMapImpl::At NewBlock" 抽取
        第一个逗号后面是时间戳，注意这个日志和上面有区别，第一个逗号后面还有个空格
        this 后面是地图的内存地址，对于这种操作，可以认为地图新开辟了一小块内存
        blockStart 后面是新开辟内存的起始坐标
        mapRange 后面是整个地图范围
          对于[0 0 1023 1023]，比例是1：1，我需要你在 gui 界面上画一个对应起点的，宽高为 64 的正方形，这个正方形用半透明色填充，还可以看到地图背景
          对于[0 0 2559 2559]，比例需要折算，起点和宽高都要除以 2.5，画一个相应起点的，宽高的正方形，这个正方形用半透明色填充，还可以看到地图背景
     d. 1242, 2614420 T3935 ClusterGridMapX::Set:652 [info] [PL6] ClusterGridMapImpl::Set NewBlock this 0x7f84c142d0 x=1201, y=1204, blockStart(1152 1152) tableIdx=738, blockCount=395, maxBlockCount=800 mapRange=[0 0 2559 2559]
       日志格式说明：
        这种日志可以通过关键字 "ClusterGridMapImpl::Set NewBlock" 抽取
        第一个逗号后面是时间戳，注意这个日志和上面有区别，第一个逗号后面还有个空格
        this 后面是地图的内存地址，对于这种操作，可以认为地图新开辟了一小块内存
        blockStart 后面是新开辟内存的起始坐标
        mapRange 后面是整个地图范围
          对于[0 0 1023 1023]，比例是1：1，我需要你在 gui 界面上画一个对应起点的，宽高为 64 的正方形，这个正方形用半透明色填充，还可以看到地图背景
          对于[0 0 2559 2559]，比例需要折算，起点和宽高都要除以 2.5，画一个相应起点的，宽高的正方形，这个正方形用半透明色填充，还可以看到地图背景
     e. 88503,4970881 T1484 SLAMAlgorithm::SLAMAlgorithm::RecordSLAMPos:132 [info] [PL9] 1650,-278,94.66
       日志格式说明：
        这种日志可以通过关键字 "SLAMAlgorithm::RecordSLAMPos" 抽取
        第一个逗号后面是时间戳
        [PL9] 后面是机器人的位置坐标，x,y,theta，不过单位是毫米，需要除以50，转换成地图上的坐标
6> 你只需要提取日志的关键信息，例如时间，地图名称，内存地址，操作类型，坐标，范围等
7> 然后在 gui 界面上显示出来当前机器所在位置，机器用一个绿色的圆表示，机器朝向可以用从机器中心伸出去的一根射线表示
8> 在 gui 界面上，需要有一个时间轴，可以鼠标拖动，看不同的时间机器的位置和内存分配的情况
9> 你可以使用任何你觉得合适的颜色和样式来，直接在操作界面有 CheckBox，可以选择某一种地图（所有需要显示的地图都在 PrintMemoryUsage 中，不在这个里面的 this 指针可能对应一个临时文件，不需要显示）
"""

import sys
import re
import math
import os
import subprocess
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar,
                             QGraphicsView, QGraphicsScene, QLabel, QSlider,
                             QCheckBox, QScrollArea, QFrame, QGroupBox, QGridLayout,
                             QToolTip, QDialog, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QPointF, QSettings, QEvent
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush, QPainterPath
import numpy as np
from src.utils.GridMapPPM import GridMapPPM


class CustomGraphicsView(QGraphicsView):
    """自定义图形视图类，用于处理鼠标移动事件"""

    def __init__(self, scene, coord_label, ppm_map_ref):
        super().__init__(scene)
        self.coord_label = coord_label
        self.ppm_map_ref = ppm_map_ref  # 使用引用来访问ppm_map

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，显示坐标"""
        # 获取鼠标在视图中的位置
        view_pos = event.pos()
        # 转换为场景坐标
        scene_pos = self.mapToScene(view_pos)

        # 转换为地图坐标系（从像素坐标到[-512, -512]到[511, 511]）
        if self.ppm_map_ref is not None and self.ppm_map_ref.mapWidth > 0:
            # 从像素坐标转换为地图坐标
            # 使用 1024 作为范围，使得中心点 (width/2, height/2) 对应 (0, 0)
            map_x = (scene_pos.x() / self.ppm_map_ref.mapWidth) * 1024 - 512
            map_y = 512 - (scene_pos.y() / self.ppm_map_ref.mapHeight) * 1024

            # 更新坐标标签
            self.coord_label.setText(f"Mouse Position: ({map_x:.1f}, {map_y:.1f})")

        # 调用父类的mouseMoveEvent以保持原有功能
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """处理鼠标点击事件，显示详细信息"""
        if event.button() == Qt.LeftButton:
            # 获取鼠标位置的所有项目
            items = self.items(event.pos())
            details = []
            for item in items:
                # 获取存储在 data(0) 中的详细信息
                data = item.data(0)
                if data:
                    details.append(data)
            
            if details:
                self.show_details_dialog(details)
                # 如果处理了点击，可以选择是否继续传递事件
                # 这里我们继续传递，以免影响其他交互（如选择）
        
        super().mousePressEvent(event)

    def show_details_dialog(self, details):
        """显示详细信息对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Memory Block Details")
        dialog.resize(800, 600) # 设置一个较大的默认大小
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        # 设置字体，方便阅读代码/堆栈
        font = text_edit.font()
        font.setFamily("Courier New")
        font.setPointSize(10)
        text_edit.setFont(font)
        
        combined_text = f"Found {len(details)} items:\n" + ("\n" + "="*50 + "\n").join(details)
        text_edit.setText(combined_text)
        
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()


class MemoryUsageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memory Usage Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # 数据存储
        self.ppm_map = None
        self.logs = []  # 存储所有解析后的日志
        self.time_logs = {}  # 按时间索引的日志
        self.maps_info = {}  # 存储地图信息
        self.robot_positions = {}  # 存储机器人位置
        self.current_time_index = 0
        self.map_checkboxes = {}
        self.loaded_log_files = set() # 存储已加载的日志文件路径
        
        # 符号解析相关
        self.pending_symbols = defaultdict(set) # 待解析的符号 {lib_name: {addr1, addr2, ...}}
        self.symbol_cache = {} # 已解析的符号 {(lib_name, addr): function_name}

        # 机器人轨迹相关
        self.robot_path_items = []  # 存储机器人轨迹图形项

        # 解析上下文
        self.last_log_entry = None
        self.expecting_stack_trace = False

        # 缓存地图Pixmap以提高性能
        self.cached_pixmap = None
        self.cached_map_width = 0
        self.cached_map_height = 0

        # 加载保存的库路径
        settings = QSettings("MemoryUsageViewer", "PathPlan")
        self.lib_path = settings.value("lib_path", "")
        print(f"Loaded lib path: {self.lib_path}")

        # 初始化UI
        self.init_ui()

    def init_ui(self):
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 加载地图按钮
        self.load_map_btn = QPushButton("Load PPM Map")
        self.load_map_btn.clicked.connect(self.load_ppm_map)
        button_layout.addWidget(self.load_map_btn)

        # 添加日志按钮
        self.add_log_btn = QPushButton("Add Log")
        self.add_log_btn.clicked.connect(self.add_log)
        button_layout.addWidget(self.add_log_btn)

        # 设置库路径按钮
        self.set_lib_path_btn = QPushButton("Set Lib Path")
        self.set_lib_path_btn.clicked.connect(self.set_lib_path)
        if self.lib_path:
            self.set_lib_path_btn.setToolTip(f"Current: {self.lib_path}")
        button_layout.addWidget(self.set_lib_path_btn)

        # 进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)

        # SetAll 开关
        self.enable_set_all_checkbox = QCheckBox("Enable SetAll Clear")
        self.enable_set_all_checkbox.setChecked(True)
        self.enable_set_all_checkbox.stateChanged.connect(lambda: self.update_display())
        button_layout.addWidget(self.enable_set_all_checkbox)

        main_layout.addLayout(button_layout)

        # 坐标显示标签
        self.coord_label = QLabel("Mouse Position: (0, 0)")
        main_layout.addWidget(self.coord_label)

        # 时间轴
        time_layout = QHBoxLayout()
        self.time_label = QLabel("Time: 0")
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(0)
        self.time_slider.valueChanged.connect(self.on_time_changed)
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.time_slider)
        main_layout.addLayout(time_layout)

        # 内容布局（水平分割：左侧地图选择，右侧地图显示）
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # 左侧：地图选择区域
        # 使用 GroupBox 和 ScrollArea 来管理地图列表
        map_group = QGroupBox("Maps Selection")
        map_group.setFixedWidth(300) # 设置固定宽度
        map_group_layout = QVBoxLayout(map_group)
        
        # 全选/全不选按钮
        map_selection_buttons_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("All")
        self.select_all_btn.clicked.connect(self.select_all_maps)
        self.deselect_all_btn = QPushButton("None")
        self.deselect_all_btn.clicked.connect(self.deselect_all_maps)
        map_selection_buttons_layout.addWidget(self.select_all_btn)
        map_selection_buttons_layout.addWidget(self.deselect_all_btn)
        map_group_layout.addLayout(map_selection_buttons_layout)

        self.map_scroll_area = QScrollArea()
        self.map_scroll_area.setWidgetResizable(True)
        # self.map_scroll_area.setMaximumHeight(150) # 不再限制高度，因为是垂直布局
        self.map_scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.map_selection_widget = QWidget()
        self.map_selection_layout = QVBoxLayout(self.map_selection_widget) # 改为垂直布局，更适合侧边栏
        self.map_selection_layout.setAlignment(Qt.AlignTop)
        
        self.map_scroll_area.setWidget(self.map_selection_widget)
        map_group_layout.addWidget(self.map_scroll_area)
        
        content_layout.addWidget(map_group)

        # 右侧：图形视图
        self.graphics_scene = QGraphicsScene()
        self.graphics_view = CustomGraphicsView(self.graphics_scene, self.coord_label, self.ppm_map)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setMouseTracking(True)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.graphics_view)
        self.scroll_area.setWidgetResizable(True)
        content_layout.addWidget(self.scroll_area, 1) # 伸缩因子1，占据剩余空间
        
        # 初始化显示默认背景
        self.display_background()

    def load_ppm_map(self):
        """加载PPM地图文件"""
        # 使用QSettings存储和获取上次目录
        settings = QSettings("MemoryUsageViewer", "PathPlan")
        last_path = settings.value("last_ppm_directory", "")

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PPM Map", last_path, "All Files (*)")

        if file_path:
            # 保存所选文件的目录
            settings.setValue("last_ppm_directory", os.path.dirname(file_path))

            self.ppm_map = GridMapPPM()
            # 不需要trim周围
            self.ppm_map.loadData(file_path, trim=False)
            self.display_map()

    def set_lib_path(self):
        """设置库文件搜索路径"""
        settings = QSettings("MemoryUsageViewer", "PathPlan")
        current_path = self.lib_path if self.lib_path else settings.value("last_ppm_directory", "")
        
        directory = QFileDialog.getExistingDirectory(
            self, "Select Library Directory", current_path)
            
        if directory:
            self.lib_path = directory
            settings.setValue("lib_path", directory)
            self.set_lib_path_btn.setToolTip(f"Current: {self.lib_path}")
            print(f"Set lib path to: {self.lib_path}")

    def display_map(self):
        """在图形视图中显示地图"""
        if self.ppm_map is None:
            return

        # 检查是否需要重新生成Pixmap
        if (self.cached_pixmap is None or
            self.cached_map_width != self.ppm_map.mapWidth or
            self.cached_map_height != self.ppm_map.mapHeight):

            # 创建QImage
            width, height = self.ppm_map.mapWidth, self.ppm_map.mapHeight
            image = QImage(width, height, QImage.Format_RGB32)

            # 填充图像数据
            for x in range(width):
                for y in range(height):
                    # 注意：PPM坐标系与QImage坐标系不同，需要转换
                    # PPM中y=0是最上面一行，而QImage中y=0是最上面一行
                    value = self.ppm_map.mapData[x][y]
                    if value == 1:  # 障碍物
                        color = QColor(0, 0, 0)  # 黑色
                    elif value == -1:  # 空闲空间
                        color = QColor(255, 255, 255)  # 白色
                    else:  # 默认
                        color = QColor(128, 128, 128)  # 灰色

                    image.setPixelColor(x, y, color)

            # 缓存Pixmap
            self.cached_pixmap = QPixmap.fromImage(image)
            self.cached_map_width = width
            self.cached_map_height = height

        # 添加Pixmap到场景
        self.graphics_scene.clear()
        self.graphics_scene.addPixmap(self.cached_pixmap)

        # 清空机器人轨迹项列表
        self.robot_path_items = []

        # 设置场景大小
        self.graphics_scene.setSceneRect(0, 0, self.cached_map_width, self.cached_map_height)

        # 更新自定义视图中的ppm_map引用
        self.graphics_view.ppm_map_ref = self.ppm_map

        # 添加坐标系信息
        self.add_coordinate_system()

    def mouse_move_event(self, event):
        """处理鼠标移动事件，显示坐标"""
        # 获取鼠标在视图中的位置
        view_pos = event.pos()
        # 转换为场景坐标
        scene_pos = self.graphics_view.mapToScene(view_pos)

        # 转换为地图坐标系（从像素坐标到[-512, -512]到[511, 511]）
        if self.ppm_map is not None:
            # 从像素坐标转换为地图坐标
            map_x = (scene_pos.x() / self.ppm_map.mapWidth) * 1023 - 512
            map_y = 511 - (scene_pos.y() / self.ppm_map.mapHeight) * 1023

            # 更新坐标标签
            self.coord_label.setText(f"Mouse Position: ({map_x:.1f}, {map_y:.1f})")

        # 调用父类的mouseMoveEvent以保持原有功能
        super(QGraphicsView, self.graphics_view).mouseMoveEvent(event)

    def add_coordinate_system(self):
        """添加坐标系信息"""
        # 地图坐标系: 左下角[-512, -512]到右上角[511, 511]
        # 需要绘制坐标轴和标签
        if self.ppm_map is None:
            return

        width, height = self.ppm_map.mapWidth, self.ppm_map.mapHeight
        pen = QPen(QColor(255, 0, 0, 128))  # 半透明红色
        pen.setWidth(2)

        # 绘制中心点(0,0)
        center_x = width // 2
        center_y = height // 2

        # 绘制坐标轴
        # X轴
        self.graphics_scene.addLine(0, center_y, width, center_y, pen)
        # Y轴
        self.graphics_scene.addLine(center_x, 0, center_x, height, pen)

        # 添加坐标标签
        # 由于这是一个示例，这里简单添加几个标签
        font = self.graphics_scene.font()
        font.setPointSize(10)

        # 中心点标签
        text = self.graphics_scene.addText("(0,0)", font)
        text.setPos(center_x + 5, center_y + 5)
        text.setDefaultTextColor(QColor(255, 0, 0, 128))

        # 添加其他标签
        text = self.graphics_scene.addText("(-512,-512)", font)
        text.setPos(5, height - 20)
        text.setDefaultTextColor(QColor(255, 0, 0, 128))

        text = self.graphics_scene.addText("(511,511)", font)
        text.setPos(width - 80, 5)
        text.setDefaultTextColor(QColor(255, 0, 0, 128))

    def add_log(self):
        """添加日志文件"""
        # 使用QSettings存储和获取上次目录
        settings = QSettings("MemoryUsageViewer", "PathPlan")
        last_path = settings.value("last_log_directory", "")

        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Log Files", last_path, "Log Files (*)")

        if file_paths:
            # 保存所选文件的目录
            settings.setValue("last_log_directory", os.path.dirname(file_paths[0]))

            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(len(file_paths))

            # 使用定时器避免界面冻结
            self.log_files = file_paths
            self.current_log_index = 0
            self.timer = QTimer()
            self.timer.timeout.connect(self.process_next_log)
            self.timer.start(100)  # 每100毫秒处理一个文件

    def process_next_log(self):
        """处理下一个日志文件"""
        if self.current_log_index < len(self.log_files):
            file_path = self.log_files[self.current_log_index]
            
            # 检查文件是否已经加载过
            if file_path not in self.loaded_log_files:
                self.parse_log_file(file_path)
                self.loaded_log_files.add(file_path)
            else:
                print(f"Skipping already loaded log file: {file_path}")
                
            self.current_log_index += 1
            self.progress_bar.setValue(self.current_log_index)
        else:
            # 处理完成
            self.timer.stop()
            self.progress_bar.setVisible(False)
            self.update_time_slider()
            self.update_map_checkboxes()
            # 确保更新显示
            self.update_display()

    def parse_log_file(self, file_path):
        """解析日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = 0
                parsed_count = 0
                self.last_log_entry = None # 重置最后一个日志条目
                
                for line in f:
                    line_count += 1
                    if self.parse_log_line(line.strip()):
                        parsed_count += 1
                
                # 解析完文件后，批量解析符号
                self.resolve_pending_symbols()
                
                print(f"Parsed {parsed_count}/{line_count} lines from {file_path}")
        except Exception as e:
            print(f"Error parsing log file {file_path}: {e}")

    def parse_log_line(self, line):
        """解析单行日志"""
        # 添加调试信息，查看是否进入此函数
        # print(f"Parsing line: {line[:100]}..." if len(line) > 100 else f"Parsing line: {line}")

        if "PrintMemoryUsage" in line:
            result = self.parse_print_memory_usage(line)
            return result
        elif "ClusterGridMapX::SetAll" in line or "ClusterMapCore::SetAll" in line:
            result = self.parse_set_all(line)
            return result
        elif "ClusterGridMapImpl::At NewBlock" in line or "ClusterMapCore::At NewBlock" in line:
            result = self.parse_at_new_block(line)
            return result
        elif "ClusterGridMapImpl::Set NewBlock" in line or "ClusterMapCore::Set NewBlock" in line:
            result = self.parse_set_new_block(line)
            return result
        elif "ClusterMapCore::ClusterMapCore" in line:
            result = self.parse_map_ctor(line)
            return result
        elif "ClusterMapCore::LogStackTrace" in line:
            result = self.parse_log_stack_trace(line)
            return result
        elif "SLAMAlgorithm::RecordSLAMPos" in line:
            result = self.parse_slam_position(line)
            return result

        # 检查是否是堆栈跟踪行
        # 格式: #1 /opt/rockrobo/cleaner/lib/librrnavdrv.so +0xc9c3bf [??] (Addr: 0x7f71eb73bf)
        stack_match = re.match(
            r'^\s*(?:#\d+|\d+>)\s+(?P<lib_path>\S+)\s+\+(?P<addr>0x[0-9a-fA-F]+)',
            line,
        )
        if stack_match:
            lib_path = stack_match.group('lib_path')
            addr = stack_match.group('addr')
            # lib_name = os.path.basename(lib_path)
            
            # 添加到待解析列表
            # 使用完整路径作为键，以便后续在 self.lib_path 中查找
            self.pending_symbols[lib_path].add(addr)
            
            # 如果有上一个日志条目，将堆栈信息添加到其中
            if self.last_log_entry is not None:
                if 'stack_trace' not in self.last_log_entry and self.expecting_stack_trace:
                    self.last_log_entry['stack_trace'] = []
                if 'stack_trace' in self.last_log_entry:
                    self.last_log_entry['stack_trace'].append({
                        'lib_name': lib_path,
                        'addr': addr,
                        'original_line': line
                    })
            self.expecting_stack_trace = True

            return True

        if self.expecting_stack_trace:
            self.expecting_stack_trace = False

        return False

    def resolve_pending_symbols(self):
        """批量解析待解析的符号"""
        if not self.lib_path or not self.pending_symbols:
            return

        print(f"Resolving symbols for {len(self.pending_symbols)} libraries...")
        
        for lib_full_path, addrs in self.pending_symbols.items():
            # 查找库文件
            # 将 lib_full_path 当作相对于根目录的路径，拼接到 self.lib_path
            # 去掉开头的 /
            relative_path = lib_full_path.lstrip('/')
            lib_file_path = os.path.join(self.lib_path, relative_path)
            
            if not os.path.exists(lib_file_path):
                lib_file_path = os.path.join(self.lib_path, os.path.basename(lib_full_path))

            if not os.path.exists(lib_file_path):
                print(f"Library not found: {lib_file_path} (original: {lib_full_path})")
                continue
                
            # 准备 llvm-symbolizer 命令
            # 使用 --inlining=false 确保每个地址只输出一个栈帧（两行），方便解析
            symbolizer_cmd = ["llvm-symbolizer", "--obj", lib_file_path, "--inlining=false"]
            
            # 将地址列表转换为排序后的列表，以便处理
            sorted_addrs = sorted(list(addrs))
            
            try:
                # 启动进程
                process = subprocess.Popen(
                    symbolizer_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 发送地址
                input_str = "\n".join(sorted_addrs)
                stdout, stderr = process.communicate(input=input_str)
                
                if process.returncode != 0:
                    print(f"llvm-symbolizer failed for {lib_full_path}: {stderr}")
                    continue
                    
                # 解析输出
                # llvm-symbolizer --inlining=false 输出格式为两行一组：函数名\n文件名:行号:列号
                lines = stdout.strip().split('\n')
                # 移除可能的空行
                lines = [l for l in lines if l.strip()]
                
                if len(lines) != len(sorted_addrs) * 2:
                    print(f"llvm-symbolizer output mismatch for {lib_full_path}: expected {len(sorted_addrs)*2} lines, got {len(lines)}")
                    continue
                    
                for i, addr in enumerate(sorted_addrs):
                    func_name = lines[i * 2]
                    file_line = lines[i * 2 + 1]
                    
                    # 存入缓存
                    self.symbol_cache[(lib_full_path, addr)] = func_name
                    print(f"Resolved {lib_full_path} {addr} -> {func_name}")
                    
            except Exception as e:
                print(f"Error resolving symbols for {lib_full_path}: {e}")
        
        # 清空待解析列表
        self.pending_symbols.clear()

    def parse_print_memory_usage(self, line):
        """解析PrintMemoryUsage日志"""
        # 示例: 1207,2614350 T3935 VisionStructLight::VisionStructLight::PrintMemoryUsage:1580 [info] [PL6] VisionObs-LOOSEWIRE map this 0x7f84c14750 range=[0 0 1023 1023] center=[0 0] use memory 0
        # 或者: 1559,3653880 T2905 VisionStructLight::VisionStructLight::PrintMemoryUsage:1623 [info] [PL6] SpaceMap map this 0x792c1a250 range=[0 0 1023 1023] use memory 0
        if "PrintMemoryUsage" not in line:
            return False

        try:
            # 找到第一个逗号的位置
            first_comma = line.find(',')
            if first_comma == -1:
                return False

            # 从第一个逗号后开始查找时间戳
            # 跳过逗号后的空格（如果有）
            start_pos = first_comma + 1
            while start_pos < len(line) and line[start_pos] == ' ':
                start_pos += 1

            # 查找下一个空格或制表符作为时间戳结束位置
            end_pos = start_pos
            while end_pos < len(line) and line[end_pos] not in [' ', '\t']:
                end_pos += 1

            # 提取时间戳
            timestamp_str = line[start_pos:end_pos]
            timestamp = float(timestamp_str)

            # 查找 PL 标签
            pl_start = line.find('[PL')
            if pl_start == -1:
                return False

            # 提取 PL 编号
            pl_end = line.find(']', pl_start)
            if pl_end == -1:
                return False

            pl_number = line[pl_start+3:pl_end]

            # 查找地图名称 (在PL标签后查找地图名称)
            # 格式: [PL6] SpaceMap map this ...
            map_name_start = pl_end + 2  # 跳过 '] '
            map_name_end = line.find(' map ', map_name_start)
            if map_name_end == -1:
                return False

            map_name = line[map_name_start:map_name_end].strip()

            # 查找 this 指针
            this_start = line.find('this ')
            if this_start == -1:
                return False

            mem_addr_start = this_start + 5  # 跳过 'this '
            mem_addr_end = line.find(' ', mem_addr_start)
            if mem_addr_end == -1:
                mem_addr_end = len(line)

            mem_addr = line[mem_addr_start:mem_addr_end].strip()

            # 查找 range
            range_start = line.find('range=[')
            if range_start == -1:
                return False

            range_start += 7  # 跳过 'range=['
            range_end = line.find(']', range_start)
            if range_end == -1:
                return False

            range_str = line[range_start:range_end]
            range_vals = list(map(int, range_str.split()))

            # 查找内存大小
            memory_start = line.find('use memory ')
            if memory_start == -1:
                return False

            memory_start += 11  # 跳过 'use memory '
            memory_end = memory_start
            while memory_end < len(line) and line[memory_end].isdigit():
                memory_end += 1

            memory_size = int(line[memory_start:memory_end])

            log_entry = {
                'type': 'memory_usage',
                'timestamp': timestamp,
                'pl_number': pl_number,
                'map_name': map_name,
                'mem_addr': mem_addr,
                'range': range_vals,
                'memory_size': memory_size
            }

            self.logs.append(log_entry)
            self.add_to_time_logs(timestamp, log_entry)

            # 更新地图信息，包括地图名称
            if mem_addr not in self.maps_info:
                self.maps_info[mem_addr] = {
                    'name': map_name,
                    'pl_number': pl_number,
                    'ranges': []
                }
            else:
                # 如果已经存在该地址的地图信息，更新地图名称
                self.maps_info[mem_addr]['name'] = map_name

            # print(f"Parsed memory usage: time={timestamp}, map={map_name}, addr={mem_addr}")
            return True
        except (ValueError, IndexError) as e:
            # 忽略无法解析的行
            print(f"Warning: Could not parse PrintMemoryUsage line: {line[:100]}... Error: {e}")
            return False

    def parse_set_all(self, line):
        """解析ClusterGridMapX::SetAll日志"""
        # 示例: 1239, 2614357 T3962 ClusterGridMapX::SetAll:384 [info] [PL6] ClusterGridMapImpl::SetAll this 0x7f80e0f610 prevBlockCount: 0 to 0, maxBlockCount 128 releaseMem 0
        # 或者: 657, 3635740 T2550 ClusterGridMapX::SetAll:384 [info] [PL6] ClusterMapCore::SetAll this 0x7f92c1a250 prevBlockCount: 0 to 0, maxBlockCount 128 releaseMem 0
        if "ClusterGridMapX::SetAll" not in line and "ClusterMapCore::SetAll" not in line:
            return False

        try:
            # 找到第一个逗号的位置
            first_comma = line.find(',')
            if first_comma == -1:
                return False

            # 从第一个逗号后开始查找时间戳
            # 跳过逗号后的空格（如果有）
            start_pos = first_comma + 1
            while start_pos < len(line) and line[start_pos] == ' ':
                start_pos += 1

            # 查找下一个空格或制表符作为时间戳结束位置
            end_pos = start_pos
            while end_pos < len(line) and line[end_pos] not in [' ', '\t']:
                end_pos += 1

            # 提取时间戳
            timestamp_str = line[start_pos:end_pos]
            timestamp = float(timestamp_str)

            # 查找 PL 标签
            pl_start = line.find('[PL')
            if pl_start == -1:
                return False

            # 提取 PL 编号
            pl_end = line.find(']', pl_start)
            if pl_end == -1:
                return False

            pl_number = line[pl_start+3:pl_end]

            # 查找 this 指针
            this_start = line.find('this ')
            if this_start == -1:
                return False

            mem_addr_start = this_start + 5  # 跳过 'this '
            mem_addr_end = line.find(' ', mem_addr_start)
            if mem_addr_end == -1:
                mem_addr_end = len(line)

            mem_addr = line[mem_addr_start:mem_addr_end].strip()

            log_entry = {
                'type': 'set_all',
                'timestamp': timestamp,
                'pl_number': pl_number,
                'mem_addr': mem_addr
            }

            self.logs.append(log_entry)
            self.add_to_time_logs(timestamp, log_entry)
            # print(f"Parsed SetAll: time={timestamp}, addr={mem_addr}")
            return True
        except (ValueError, IndexError) as e:
            # 忽略无法解析的行
            print(f"Warning: Could not parse SetAll line: {line[:100]}... Error: {e}")
            return False

    def parse_at_new_block(self, line):
        """解析ClusterGridMapImpl::At NewBlock日志"""
        # 示例: 1240, 2614357 T3962 ClusterGridMapX::At:338 [info] [PL6] ClusterGridMapImpl::At NewBlock this 0x7f84c13310 x=515, y=509, blockStart(512 448) tableIdx=120, blockCount=53, maxBlockCount=128, mapRange=[0 0 1023 1023]
        # 或者: 1240, 2614357 T3962 ClusterGridMapX::At:338 [info] [PL6] ClusterMapCore::At NewBlock this 0x7f84c13310 x=515, y=509, blockStart(512 448) tableIdx=120, blockCount=53, maxBlockCount=128, mapRange=[0 0 1023 1023]
        if "ClusterGridMapImpl::At NewBlock" not in line and "ClusterMapCore::At NewBlock" not in line:
            return False

        try:
            # 找到第一个逗号的位置
            first_comma = line.find(',')
            if first_comma == -1:
                return False

            # 从第一个逗号后开始查找时间戳
            start_pos = first_comma + 1
            while start_pos < len(line) and line[start_pos] == ' ':
                start_pos += 1
            end_pos = start_pos
            while end_pos < len(line) and line[end_pos] not in [' ', '\t']:
                end_pos += 1
            timestamp = float(line[start_pos:end_pos])

            # 查找 PL 标签
            pl_start = line.find('[PL')
            if pl_start == -1:
                return False
            pl_end = line.find(']', pl_start)
            if pl_end == -1:
                return False
            pl_number = line[pl_start+3:pl_end]

            # 查找 this 指针
            this_start = line.find('this ')
            if this_start == -1:
                return False
            mem_addr_start = this_start + 5
            mem_addr_end = line.find(' ', mem_addr_start)
            if mem_addr_end == -1:
                mem_addr_end = len(line)
            mem_addr = line[mem_addr_start:mem_addr_end].strip()

            # 查找 blockStart
            block_start_start = line.find('blockStart(')
            if block_start_start == -1:
                return False
            block_start_start += 11
            block_start_end = line.find(')', block_start_start)
            if block_start_end == -1:
                return False
            block_start_str = line[block_start_start:block_start_end]
            block_start_coords = list(map(int, block_start_str.split()))

            # 查找 mapRange
            range_start = line.find('mapRange=[')
            if range_start == -1:
                return False
            range_start += 10
            range_end = line.find(']', range_start)
            if range_end == -1:
                return False
            range_str = line[range_start:range_end]
            range_vals = list(map(int, range_str.split()))

            log_entry = {
                'type': 'at_new_block',
                'timestamp': timestamp,
                'pl_number': pl_number,
                'mem_addr': mem_addr,
                'block_start': (block_start_coords[0], block_start_coords[1]),
                'range': range_vals,
                'stack_trace': [] # 初始化堆栈跟踪列表
            }

            self.logs.append(log_entry)
            self.add_to_time_logs(timestamp, log_entry)
            self.last_log_entry = log_entry # 记录为最后一个日志条目

            # 更新地图信息
            if mem_addr not in self.maps_info:
                self.maps_info[mem_addr] = {
                    'pl_number': pl_number,
                    'ranges': []
                }
            self.maps_info[mem_addr]['ranges'].append({
                'timestamp': timestamp,
                'block_start': (block_start_coords[0], block_start_coords[1]),
                'range': range_vals,
                'stack_trace': log_entry['stack_trace'] # 共享堆栈跟踪列表
            })
            
            # print(f"Parsed At NewBlock: time={timestamp}, addr={mem_addr}")
            return True
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse At NewBlock line: {line[:100]}... Error: {e}")
            return False

    def parse_set_new_block(self, line):
        """解析ClusterGridMapImpl::Set NewBlock日志"""
        # 示例: 1242, 2614420 T3935 ClusterGridMapX::Set:652 [info] [PL6] ClusterGridMapImpl::Set NewBlock this 0x7f84c142d0 x=1201, y=1204, blockStart(1152 1152) tableIdx=738, blockCount=395, maxBlockCount=800 mapRange=[0 0 2559 2559]
        # 或者: 1377, 3653145 T2854 ClusterGridMapX::Set:652 [info] [PL6] ClusterMapCore::Set NewBlock this 0x7f92c1a250 x=539, y=491, blockStart(512 448) tableIdx=120, blockCount=1, maxBlockCount=128 mapRange=[0 0 1023 1023]
        if "ClusterGridMapImpl::Set NewBlock" not in line and "ClusterMapCore::Set NewBlock" not in line:
            return False

        try:
            # 找到第一个逗号的位置
            first_comma = line.find(',')
            if first_comma == -1:
                return False

            # 从第一个逗号后开始查找时间戳
            # 跳过逗号后的空格（如果有）
            start_pos = first_comma + 1
            while start_pos < len(line) and line[start_pos] == ' ':
                start_pos += 1

            # 查找下一个空格或制表符作为时间戳结束位置
            end_pos = start_pos
            while end_pos < len(line) and line[end_pos] not in [' ', '\t']:
                end_pos += 1

            # 提取时间戳
            timestamp_str = line[start_pos:end_pos]
            timestamp = float(timestamp_str)

            # 查找 PL 标签
            pl_start = line.find('[PL')
            if pl_start == -1:
                return False

            # 提取 PL 编号
            pl_end = line.find(']', pl_start)
            if pl_end == -1:
                return False

            pl_number = line[pl_start+3:pl_end]

            # 查找 this 指针
            this_start = line.find('this ')
            if this_start == -1:
                return False

            mem_addr_start = this_start + 5  # 跳过 'this '
            mem_addr_end = line.find(' ', mem_addr_start)
            if mem_addr_end == -1:
                mem_addr_end = len(line)

            mem_addr = line[mem_addr_start:mem_addr_end].strip()

            # 查找 blockStart
            block_start_start = line.find('blockStart(')
            if block_start_start == -1:
                return False

            block_start_start += 11  # 跳过 'blockStart('
            block_start_end = line.find(')', block_start_start)
            if block_start_end == -1:
                return False

            block_start_str = line[block_start_start:block_start_end]
            block_start_coords = list(map(int, block_start_str.split()))

            # 查找 mapRange
            range_start = line.find('mapRange=[')
            if range_start == -1:
                return False

            range_start += 10  # 跳过 'mapRange=['
            range_end = line.find(']', range_start)
            if range_end == -1:
                return False

            range_str = line[range_start:range_end]
            range_vals = list(map(int, range_str.split()))

            log_entry = {
                'type': 'set_new_block',
                'timestamp': timestamp,
                'pl_number': pl_number,
                'mem_addr': mem_addr,
                'block_start': (block_start_coords[0], block_start_coords[1]),
                'range': range_vals,
                'stack_trace': [] # 初始化堆栈跟踪列表
            }

            self.logs.append(log_entry)
            self.add_to_time_logs(timestamp, log_entry)
            self.last_log_entry = log_entry # 记录为最后一个日志条目

            # 更新地图信息
            if mem_addr not in self.maps_info:
                self.maps_info[mem_addr] = {
                    'pl_number': pl_number,
                    'ranges': []
                }
            self.maps_info[mem_addr]['ranges'].append({
                'timestamp': timestamp,
                'block_start': (block_start_coords[0], block_start_coords[1]),
                'range': range_vals,
                'stack_trace': log_entry['stack_trace'] # 共享堆栈跟踪列表
            })

            # print(f"Parsed Set NewBlock: time={timestamp}, addr={mem_addr}, block_start=({block_start_coords[0]}, {block_start_coords[1]})")
            return True
        except (ValueError, IndexError) as e:
            # 忽略无法解析的行
            print(f"Warning: Could not parse Set NewBlock line: {line[:100]}... Error: {e}")
            return False

    def parse_slam_position(self, line):
        """解析SLAMAlgorithm::RecordSLAMPos日志"""
        # 示例: 88503,4970881 T1484 SLAMAlgorithm::SLAMAlgorithm::RecordSLAMPos:132 [info] [PL9] 1650,-278,94.66
        # 或者: 91580, 5028719 T2570 SLAMAlgorithm::SLAMAlgorithm::RecordSLAMPos:132 [info] [PL9] 1,528,-89.90
        # 或者(紧凑格式，多条在同一行):
        # 4958,415208,1221,6,2,SLAMAlgorithm::SLAMAlgorithm::RecordSLAMPos:132 0,0,0.00 ...

        if "SLAMAlgorithm::RecordSLAMPos" not in line:
            return False

        try:
            compact_re = re.compile(
                r"(?:^|\s)(?P<first>\d+),(?P<timestamp>\d+),\d+,\d+,\d,"
                r"SLAMAlgorithm::SLAMAlgorithm::RecordSLAMPos:132\s+"
                r"(?P<x>-?\d+),(?P<y>-?\d+),(?P<theta>-?\d+(?:\.\d+)?)"
            )

            found_any = False
            for match in compact_re.finditer(line):
                timestamp = float(match.group("timestamp"))
                x = int(match.group("x"))
                y = int(match.group("y"))
                theta = float(match.group("theta"))

                x_map = x / 50.0
                y_map = y / 50.0

                log_entry = {
                    'type': 'robot_position',
                    'timestamp': timestamp,
                    'pl_number': '',
                    'x': x_map,
                    'y': y_map,
                    'theta': theta
                }

                self.logs.append(log_entry)
                self.add_to_time_logs(timestamp, log_entry)
                self.robot_positions[timestamp] = (x_map, y_map, theta)
                found_any = True

            if found_any:
                return True

            first_comma = line.find(',')
            if first_comma == -1:
                return False

            start_pos = first_comma + 1
            while start_pos < len(line) and line[start_pos] == ' ':
                start_pos += 1

            end_pos = start_pos
            while end_pos < len(line) and line[end_pos] not in [' ', '\t']:
                end_pos += 1

            timestamp = float(line[start_pos:end_pos])

            pl_start = line.find('[PL')
            if pl_start == -1:
                return False

            pl_end = line.find(']', pl_start)
            if pl_end == -1:
                return False

            pl_number = line[pl_start + 3:pl_end]

            coords_start = pl_end + 2
            coords_part = line[coords_start:].strip()

            coords = coords_part.split(',')
            if len(coords) < 3:
                return False

            x = int(coords[0])
            y = int(coords[1])
            theta = float(coords[2])

            x_map = x / 50.0
            y_map = y / 50.0

            log_entry = {
                'type': 'robot_position',
                'timestamp': timestamp,
                'pl_number': pl_number,
                'x': x_map,
                'y': y_map,
                'theta': theta
            }

            self.logs.append(log_entry)
            self.add_to_time_logs(timestamp, log_entry)
            self.robot_positions[timestamp] = (x_map, y_map, theta)
            return True
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse robot position line: {line[:100]}... Error: {e}")
            return False

    def parse_map_ctor(self, line):
        """解析ClusterMapCore构造函数日志"""
        # 示例: 4125, 411689 T1862 ClusterMapCore::ClusterMapCore:176 [info] [PL6] ClusterMapCore ctor : this=0x7fb6888fe0 mode=2 mapRange=[-512 -512 511 511]
        if "ClusterMapCore::ClusterMapCore" not in line:
            return False

        try:
            first_comma = line.find(',')
            if first_comma == -1:
                return False

            start_pos = first_comma + 1
            while start_pos < len(line) and line[start_pos] == ' ':
                start_pos += 1

            end_pos = start_pos
            while end_pos < len(line) and line[end_pos] not in [' ', '\t']:
                end_pos += 1

            timestamp = float(line[start_pos:end_pos])

            pl_start = line.find('[PL')
            if pl_start == -1:
                return False

            pl_end = line.find(']', pl_start)
            if pl_end == -1:
                return False

            pl_number = line[pl_start + 3:pl_end]

            this_start = line.find('this=')
            if this_start == -1:
                return False

            mem_addr_start = this_start + 5
            mem_addr_end = line.find(' ', mem_addr_start)
            if mem_addr_end == -1:
                mem_addr_end = len(line)

            mem_addr = line[mem_addr_start:mem_addr_end].strip()

            range_start = line.find('mapRange=[')
            if range_start == -1:
                return False
            range_start += 10
            range_end = line.find(']', range_start)
            if range_end == -1:
                return False

            range_vals = list(map(int, line[range_start:range_end].split()))

            log_entry = {
                'type': 'map_ctor',
                'timestamp': timestamp,
                'pl_number': pl_number,
                'mem_addr': mem_addr,
                'range': range_vals,
                'stack_trace': []
            }

            self.logs.append(log_entry)
            self.add_to_time_logs(timestamp, log_entry)
            self.last_log_entry = log_entry
            self.expecting_stack_trace = False

            if mem_addr not in self.maps_info:
                self.maps_info[mem_addr] = {
                    'name': 'ClusterMapCore',
                    'pl_number': pl_number,
                    'ranges': []
                }

            return True
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse ClusterMapCore ctor line: {line[:100]}... Error: {e}")
            return False

    def parse_log_stack_trace(self, line):
        """解析ClusterMapCore::LogStackTrace日志"""
        # 示例: 4126, 411694 T1862 ClusterMapCore::LogStackTrace:33 [info] [PL6] Stack Trace:
        if "ClusterMapCore::LogStackTrace" not in line:
            return False

        self.expecting_stack_trace = True
        return True

    def add_to_time_logs(self, timestamp, log_entry):
        """将日志添加到时间索引中"""
        if timestamp not in self.time_logs:
            self.time_logs[timestamp] = []
        self.time_logs[timestamp].append(log_entry)
        # print(f"Added log entry at timestamp {timestamp}")

    def update_time_slider(self):
        """更新时间滑块"""
        if self.time_logs:
            timestamps = sorted(self.time_logs.keys())
            self.time_slider.setMinimum(0)
            self.time_slider.setMaximum(len(timestamps) - 1)
            # 设置初始值为第一个时刻，而不是最后一个
            self.time_slider.setValue(0)
            print(f"Updated time slider: {len(timestamps)} timestamps found, range: {timestamps[0]} to {timestamps[-1]}")
            # 立即更新显示
            if len(timestamps) > 0:
                self.current_time_index = 0  # 修改为0而不是最后一个
                self.time_label.setText(f"Time: {timestamps[0]}")
                self.update_display()
        else:
            print("No time logs found")

    def select_all_maps(self):
        """全选地图"""
        self.set_all_maps_checked(True)

    def deselect_all_maps(self):
        """全不选地图"""
        self.set_all_maps_checked(False)

    def set_all_maps_checked(self, checked):
        """设置所有地图复选框的选中状态"""
        # 阻止信号以避免多次更新
        for checkbox in self.map_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
        
        # 更新显示一次
        self.update_display()

    def update_map_checkboxes(self):
        """更新地图选择复选框"""
        # 清除现有复选框
        while self.map_selection_layout.count():
            item = self.map_selection_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 添加新的复选框
        self.map_checkboxes = {}
        
        # 按地址排序，保证顺序一致
        sorted_maps = sorted(self.maps_info.items(), key=lambda x: x[0])
        
        for addr, info in sorted_maps:
            name = info.get('name', f"Map {addr}")
            # 截断过长的名字
            display_name = f"{name} ({addr})"
            if len(display_name) > 35:
                display_name = display_name[:32] + "..."
                
            checkbox = QCheckBox(display_name)
            checkbox.setToolTip(f"{name} ({addr})") # 完整名字在 tooltip 显示
            checkbox.setChecked(True)
            checkbox.mem_addr = addr
            checkbox.stateChanged.connect(lambda: self.update_display())
            
            self.map_selection_layout.addWidget(checkbox)
            self.map_checkboxes[addr] = checkbox
                
        print(f"Updated map checkboxes: {len(self.maps_info)} maps found")

    def on_time_changed(self, value):
        """时间滑块值改变时的处理函数"""
        # 使用timer来延迟处理，避免滑动过程中频繁更新
        if hasattr(self, '_timer'):
            self._timer.stop()
        else:
            self._timer = QTimer()
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self._update_display)

        self._slider_value = value
        self._timer.start(100)  # 延迟100ms更新

    def _update_display(self):
        """延迟更新显示"""
        value = self._slider_value
        print(f"Time slider changed to value: {value}")
        if self.time_logs:
            timestamps = sorted(self.time_logs.keys())
            if 0 <= value < len(timestamps):
                timestamp = timestamps[value]
                self.time_label.setText(f"Time: {timestamp:.0f}")
                self.current_time_index = value
                self.update_display()
        else:
            print("No time logs available")

    def update_display(self):
        """更新显示内容"""
        print(f"Updating display, time_logs count: {len(self.time_logs)}, robot_positions count: {len(self.robot_positions)}")
        # 这里应该根据当前时间更新地图上的内容显示
        # 包括机器人的位置和内存块的显示

        # 总是重新显示背景（如果有地图就显示地图，否则显示默认背景）
        self.display_background()

        # 获取当前时间戳
        timestamps = sorted(self.time_logs.keys()) if self.time_logs else []
        if 0 <= self.current_time_index < len(timestamps):
            current_timestamp = timestamps[self.current_time_index]
            print(f"Displaying data for timestamp: {current_timestamp}")

            # 绘制动态元素
            self.refresh_dynamic_elements(current_timestamp)
        else:
            # 如果没有时间日志，但有机器人位置，也尝试显示
            if self.robot_positions:
                latest_time = max(self.robot_positions.keys())
                print(f"No time logs, displaying latest robot position for timestamp: {latest_time}")
                self.refresh_dynamic_elements(latest_time)
            else:
                print(f"Invalid time index: {self.current_time_index} or no timestamps")

    def refresh_dynamic_elements(self, timestamp):
        """刷新动态元素（机器人位置、内存块等）"""
        print(f"Refreshing dynamic elements for timestamp: {timestamp}")
        try:
            # 绘制内存块
            self.draw_memory_blocks(timestamp)

            # 绘制机器人位置和轨迹
            self.draw_robot_position(timestamp)
            self.draw_robot_path(timestamp)
            print("Finished refreshing dynamic elements")
        except Exception as e:
            print(f"Error refreshing dynamic elements: {e}")
            import traceback
            traceback.print_exc()

    def draw_memory_blocks(self, timestamp):
        """绘制内存块"""
        try:
            # 遍历所有已注册的地图
            for mem_addr, map_info in self.maps_info.items():
                # 检查地图是否有对应的checkbox且被选中
                if mem_addr in self.map_checkboxes and self.map_checkboxes[mem_addr].isChecked():
                    # 找到该地图最近一次 SetAll（清空）事件的时间戳
                    last_clear_time = 0
                    
                    # 只有当 SetAll 开关打开时，才计算 last_clear_time
                    if self.enable_set_all_checkbox.isChecked():
                        # 遍历所有时间日志，查找该地图的 SetAll 事件
                        for time_key in self.time_logs:
                            if time_key <= timestamp:
                                for log_entry in self.time_logs[time_key]:
                                    if (log_entry.get('type') == 'set_all' and
                                        log_entry.get('mem_addr') == mem_addr):
                                        last_clear_time = max(last_clear_time, time_key)

                    # 使用集合去重，确保每个位置只绘制一次
                    drawn_positions = set()
                    
                    # 绘制该地图的所有在当前时间戳之前分配的内存块
                    for block_info in map_info.get('ranges', []):
                        # 只绘制在最近清空之后且在当前时间之前的内存块
                        if block_info['timestamp'] > last_clear_time and block_info['timestamp'] <= timestamp:
                            # 使用 (block_start, range) 作为唯一标识
                            position_key = (block_info['block_start'], tuple(block_info['range']))
                            if position_key not in drawn_positions:
                                self.draw_single_block(block_info)
                                drawn_positions.add(position_key)
        except Exception as e:
            print(f"Error drawing memory blocks: {e}")
            import traceback
            traceback.print_exc()

    def draw_single_block(self, block_info):
        """绘制单个内存块"""
        try:
            block_start = block_info['block_start']
            map_range = block_info['range']

            # 计算比例因子
            # map_range格式: [min_x, min_y, max_x, max_y]
            range_width = map_range[2] - map_range[0]
            range_height = map_range[3] - map_range[1]

            # 根据地图范围确定比例因子
            scale_factor = 1.0
            center_offset = 512
            
            if range_width > 2000: # 假设大于2000的是大地图
                # 比例需要折算，起点和宽高都要除以2.5
                scale_factor = 2.5
                center_offset = 1280 # 2560 / 2
            
            # 如果起点是负数，说明已经是中心坐标系，不需要偏移
            if map_range[0] < 0:
                center_offset = 0

            # 计算在地图上的位置
            # blockStart是相对于mapRange的坐标，需要减去中心偏移转换到[-512, 511]坐标系
            # 注意：这里的坐标转换逻辑需要根据实际情况调整
            # 假设 block_start 是相对于地图左上角或左下角的像素坐标
            
            # 块的宽高（固定64像素，根据比例缩放）
            block_width = 64 / scale_factor
            block_height = 64 / scale_factor
            
            block_x = (block_start[0] - center_offset) / scale_factor
            block_y = (block_start[1] - center_offset) / scale_factor

            # 转换为显示坐标系
            map_to_use = self.ppm_map if self.ppm_map is not None else getattr(self, 'default_map', None)
            
            if map_to_use is not None:
                # mapWidth/1024 是为了适应当前显示的地图缩放
                display_x = (block_x + 512) * (map_to_use.mapWidth / 1024)
                display_y = (512 - block_y) * (map_to_use.mapHeight / 1024)
                display_width = block_width * (map_to_use.mapWidth / 1024)
                display_height = block_height * (map_to_use.mapHeight / 1024)

                # 绘制半透明矩形
                pen = QPen(QColor(0, 0, 255, 100))
                brush = QBrush(QColor(0, 0, 255, 50))
                # blockStart 是左下角，Qt坐标系Y轴向下，所以需要向上画（减去高度）
                rect_item = self.graphics_scene.addRect(display_x, display_y - display_height, display_width, display_height, pen, brush)
                
                # 构建 Tooltip 显示堆栈信息
                detail_text = f"Time: {block_info.get('timestamp', 0)}\n"
                detail_text += f"Block: {block_info.get('block_start')}\n"
                
                stack_trace = block_info.get('stack_trace', [])
                if stack_trace:
                    detail_text += "\nStack Trace:\n"
                    for frame in stack_trace:
                        lib = frame['lib_name']
                        addr = frame['addr']
                        # 尝试获取解析后的符号
                        func_name = self.symbol_cache.get((lib, addr), "??")
                        lib_short = os.path.basename(lib)
                        detail_text += f"{lib_short} {addr} {func_name}\n"
                
                # 设置简短的 Tooltip
                rect_item.setToolTip("Click to view Stack Trace")
                # 存储详细信息到 data(0)
                rect_item.setData(0, detail_text)
                
                # print(f"Drawn memory block at ({display_x:.1f}, {display_y:.1f})")
        except Exception as e:
            print(f"Error drawing single block: {e}")

    def draw_robot_position(self, timestamp):
        """绘制机器人位置"""
        try:
            if not self.robot_positions:
                return

            # 找到当前时间点最近的机器人位置
            closest_time = -1
            closest_pos = None
            
            # 遍历查找最近的时间点
            for t, pos in self.robot_positions.items():
                if t <= timestamp:
                    if t > closest_time:
                        closest_time = t
                        closest_pos = pos
            
            if closest_pos:
                x, y, theta = closest_pos
                
                # 使用实际的地图尺寸或者默认尺寸
                map_to_use = self.ppm_map if self.ppm_map is not None else getattr(self, 'default_map', None)
                if map_to_use is None:
                    return

                # 转换为显示坐标系
                display_x = (x + 512) * (map_to_use.mapWidth / 1024)
                display_y = (512 - y) * (map_to_use.mapHeight / 1024)  # 翻转Y轴

                # 绘制红色圆圈表示机器人
                pen = QPen(QColor(255, 0, 0))
                brush = QBrush(QColor(255, 0, 0, 200))  # 红色半透明画刷
                pen.setWidth(2)
                self.graphics_scene.addEllipse(display_x - 10, display_y - 10, 20, 20, pen, brush)
                
                # 绘制方向指示线
                line_length = 25
                rad = math.radians(theta)
                end_x = display_x + line_length * math.cos(rad)
                end_y = display_y - line_length * math.sin(rad) # Y轴翻转，sin取反? 
                # 注意：如果Y轴向下增加，而角度是逆时针增加，则sin需要取反。
                # 这里假设theta是标准的数学角度（逆时针为正），而屏幕坐标Y向下。
                # 如果Y轴向上（地图坐标），则 end_y = y + sin(theta). 
                # 转换到屏幕坐标： screen_y = H - (y + sin(theta)) = (H-y) - sin(theta) = display_y - sin(theta)
                
                pen_line = QPen(QColor(0, 255, 0))
                pen_line.setWidth(3)
                self.graphics_scene.addLine(display_x, display_y, end_x, end_y, pen_line)
                
        except Exception as e:
            print(f"Error drawing robot position: {e}")

    def draw_robot_path(self, current_timestamp):
        """绘制机器人轨迹"""
        try:
            if not self.robot_positions:
                return

            # 使用实际的地图尺寸或者默认尺寸
            map_to_use = self.ppm_map if self.ppm_map is not None else getattr(self, 'default_map', None)
            if map_to_use is None:
                return

            path_points = []
            last_point = None
            
            # 获取按时间排序的位置列表
            sorted_times = sorted(self.robot_positions.keys())
            
            for time in sorted_times:
                if time <= current_timestamp:
                    x, y, _ = self.robot_positions[time]
                    # 转换为显示坐标系
                    display_x = (x + 512) * (map_to_use.mapWidth / 1024)
                    display_y = (512 - y) * (map_to_use.mapHeight / 1024)
                    current_point = (display_x, display_y)

                    # 避免添加重复点
                    if last_point is None or abs(current_point[0] - last_point[0]) > 1.0 or abs(current_point[1] - last_point[1]) > 1.0:
                        path_points.append(current_point)
                        last_point = current_point

            if len(path_points) > 1:
                # 使用QPainterPath绘制连续的轨迹线
                path = QPainterPath()
                path.moveTo(path_points[0][0], path_points[0][1])
                
                for i in range(1, len(path_points)):
                    path.lineTo(path_points[i][0], path_points[i][1])

                pen = QPen(QColor(0, 255, 0, 150)) # 绿色半透明
                pen.setWidth(2)
                self.graphics_scene.addPath(path, pen)
                
        except Exception as e:
            print(f"Error drawing robot path: {e}")
            import traceback
            traceback.print_exc()



    def display_background(self):
        """显示背景（地图或默认背景）"""
        if self.ppm_map is not None:
            # 显示PPM地图
            self.display_map()
        else:
            # 显示默认背景
            self.display_default_background()

    def display_default_background(self):
        """显示默认背景（用于没有加载地图时显示机器人轨迹）"""
        # 清除场景
        self.graphics_scene.clear()

        # 设置默认场景大小（模拟地图大小）
        width, height = 1024, 1024
        self.graphics_scene.setSceneRect(0, 0, width, height)

        # 绘制网格线
        pen = QPen(QColor(200, 200, 200, 100))
        pen.setWidth(1)

        grid_size = 50
        
        # 计算起始偏移，使得网格线经过中心
        center_x = width / 2
        center_y = height / 2
        start_x = int(center_x % grid_size)
        start_y = int(center_y % grid_size)

        for x in range(start_x, width, grid_size):
            self.graphics_scene.addLine(x, 0, x, height, pen)
        for y in range(start_y, height, grid_size):
            self.graphics_scene.addLine(0, y, width, y, pen)

        # 绘制中心线（X轴和Y轴）
        pen = QPen(QColor(255, 0, 0, 128))
        pen.setWidth(2)
        self.graphics_scene.addLine(0, height/2, width, height/2, pen)  # X轴
        self.graphics_scene.addLine(width/2, 0, width/2, height, pen)  # Y轴

        # 添加坐标标签
        font = self.graphics_scene.font()
        font.setPointSize(10)

        # 中心点标签
        text = self.graphics_scene.addText("(0,0)", font)
        text.setPos(width/2 + 5, height/2 + 5)
        text.setDefaultTextColor(QColor(255, 0, 0, 128))

        # 角落标签
        text = self.graphics_scene.addText("(-512,-512)", font)
        text.setPos(5, height - 20)
        text.setDefaultTextColor(QColor(255, 0, 0, 128))

        text = self.graphics_scene.addText("(511,511)", font)
        text.setPos(width - 80, 5)
        text.setDefaultTextColor(QColor(255, 0, 0, 128))

        # 设置默认的ppm_map尺寸，以便坐标转换可以正常工作
        class DefaultMap:
            def __init__(self):
                self.mapWidth = 1024
                self.mapHeight = 1024

        self.default_map = DefaultMap()
        
        # 更新 graphics_view 的引用，以便鼠标坐标显示正常
        self.graphics_view.ppm_map_ref = self.default_map

# python
def main():
    app = QApplication(sys.argv)
    viewer = MemoryUsageViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
