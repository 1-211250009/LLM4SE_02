#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Main Window
主窗口界面
"""

import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QSplitter, QMenuBar, QMenu, QFileDialog, 
                               QMessageBox, QStatusBar, QToolBar, QPushButton, QLabel)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from .image_list_widget import ImageListWidget
from .preview_widget import PreviewWidget


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Photo Watermark 2")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：图片列表
        self.image_list_widget = ImageListWidget()
        self.image_list_widget.setMinimumWidth(350)
        self.image_list_widget.setMaximumWidth(500)
        
        # 右侧：预览和控制面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 预览组件
        self.preview_widget = PreviewWidget()
        
        # 临时控制面板占位
        control_panel = QWidget()
        control_panel.setFixedHeight(200)
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        control_label = QLabel("水印控制面板（待开发）")
        control_label.setAlignment(Qt.AlignCenter)
        control_label.setStyleSheet("color: #666; font-size: 14px;")
        control_layout = QVBoxLayout(control_panel)
        control_layout.addWidget(control_label)
        
        right_layout.addWidget(self.preview_widget)
        right_layout.addWidget(control_panel)
        
        # 添加到分割器
        splitter.addWidget(self.image_list_widget)
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 0)  # 左侧固定宽度
        splitter.setStretchFactor(1, 1)  # 右侧可伸缩
        
        main_layout.addWidget(splitter)
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 添加图片
        add_images_action = QAction("添加图片...", self)
        add_images_action.setShortcut("Ctrl+O")
        add_images_action.triggered.connect(self.add_images)
        file_menu.addAction(add_images_action)
        
        # 添加文件夹
        add_folder_action = QAction("添加文件夹...", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self.add_folder)
        file_menu.addAction(add_folder_action)
        
        file_menu.addSeparator()
        
        # 导出图片
        export_action = QAction("导出图片...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_images)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 添加图片按钮
        add_images_btn = QPushButton("添加图片")
        add_images_btn.clicked.connect(self.add_images)
        toolbar.addWidget(add_images_btn)
        
        # 添加文件夹按钮
        add_folder_btn = QPushButton("添加文件夹")
        add_folder_btn.clicked.connect(self.add_folder)
        toolbar.addWidget(add_folder_btn)
        
        toolbar.addSeparator()
        
        # 导出图片按钮
        export_btn = QPushButton("导出图片")
        export_btn.clicked.connect(self.export_images)
        toolbar.addWidget(export_btn)
    
    def setup_statusbar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def connect_signals(self):
        """连接信号槽"""
        # 图片列表信号
        self.image_list_widget.image_selected.connect(self.on_image_selected)
        self.image_list_widget.images_dropped.connect(self.on_images_dropped)
    
    def add_images(self):
        """添加图片文件"""
        file_manager = self.image_list_widget.get_file_manager()
        file_filter = file_manager.get_supported_formats_filter()
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片文件", "", file_filter
        )
        
        if files:
            self.image_list_widget.add_images(files)
            self.status_bar.showMessage(f"尝试添加 {len(files)} 个文件")
    
    def add_folder(self):
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择图片文件夹"
        )
        
        if folder:
            self.image_list_widget.add_images([folder])
            self.status_bar.showMessage(f"添加文件夹: {folder}")
    
    def export_images(self):
        """导出图片（临时功能，阶段1暂时简化）"""
        file_manager = self.image_list_widget.get_file_manager()
        if file_manager.get_image_count() == 0:
            QMessageBox.warning(self, "警告", "没有可导出的图片")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self, "选择输出文件夹"
        )
        
        if output_dir:
            # 验证输出目录
            is_valid, error_msg = file_manager.validate_output_directory(output_dir)
            if not is_valid:
                QMessageBox.warning(self, "警告", error_msg)
                return
            
            QMessageBox.information(self, "提示", 
                f"导出功能将在后续阶段完善\n选择的输出目录: {output_dir}")
    
    def on_image_selected(self, index: int):
        """图片被选中"""
        file_manager = self.image_list_widget.get_file_manager()
        image_info = file_manager.get_image_info(index)
        
        if image_info:
            self.preview_widget.load_image(image_info['path'])
            self.status_bar.showMessage(f"预览: {image_info['filename']}")
    
    def on_images_dropped(self, files: list):
        """文件被拖放"""
        self.image_list_widget.add_images(files)
        self.status_bar.showMessage(f"拖放添加 {len(files)} 个项目")
    
    def show_about(self):
        """显示关于信息"""
        QMessageBox.about(self, "关于 Photo Watermark 2", 
            "Photo Watermark 2\n\n"
            "版本: 1.0.0\n"
            "一个简单易用的图片水印工具\n\n"
            "支持格式: JPEG, PNG, BMP, TIFF\n"
            "支持文本和图片水印")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止缩略图加载线程
        if hasattr(self.image_list_widget, 'thumbnail_loader'):
            loader = self.image_list_widget.thumbnail_loader
            if loader and loader.isRunning():
                loader.stop()
                loader.wait()
        
        event.accept()
