#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Main Window
主窗口界面
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Photo Watermark 2")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 临时占位标签
        temp_label = QLabel("Photo Watermark 2 - 项目初始化完成")
        temp_label.setAlignment(Qt.AlignCenter)
        temp_label.setStyleSheet("font-size: 18px; padding: 20px;")
        
        main_layout.addWidget(temp_label)
