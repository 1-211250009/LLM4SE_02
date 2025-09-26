#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Image List Widget
图片列表显示组件
"""

import os
from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QListWidgetItem, QLabel, QPushButton, QSizePolicy,
                               QFrame, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, Signal, QThread, QSize
from PySide6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent

from core.file_manager import FileManager
from core.image_processor import ImageProcessor


class ThumbnailLoader(QThread):
    """缩略图加载线程"""
    thumbnail_ready = Signal(int, QPixmap)
    progress_updated = Signal(int, int)
    
    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager
        self.image_processor = ImageProcessor()
        self.should_stop = False
    
    def run(self):
        """运行缩略图加载任务"""
        images = self.file_manager.get_image_list()
        total = len(images)
        
        for i, img_info in enumerate(images):
            if self.should_stop:
                break
            
            try:
                # 加载原图
                image = self.image_processor.load_image(img_info['path'])
                if image:
                    # 创建缩略图
                    thumbnail = self.image_processor.create_thumbnail(image)
                    
                    # 转换为QPixmap
                    import io
                    buffer = io.BytesIO()
                    
                    # 根据模式选择保存格式
                    if thumbnail.mode == 'RGBA':
                        thumbnail.save(buffer, format='PNG')
                    else:
                        # 转换为RGB并保存为JPEG
                        if thumbnail.mode != 'RGB':
                            thumbnail = thumbnail.convert('RGB')
                        thumbnail.save(buffer, format='JPEG', quality=85)
                    
                    buffer.seek(0)
                    
                    # 从字节流创建QPixmap
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    self.thumbnail_ready.emit(i, pixmap)
                
                self.progress_updated.emit(i + 1, total)
                
            except Exception as e:
                print(f"加载缩略图失败 {img_info['path']}: {e}")
    
    def stop(self):
        """停止加载"""
        self.should_stop = True


class ImageListItem(QWidget):
    """图片列表项"""
    
    def __init__(self, image_info: dict, index: int):
        super().__init__()
        self.image_info = image_info
        self.index = index
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 缩略图标签
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(80, 80)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
        """)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setText("加载中...")
        
        # 信息区域
        info_layout = QVBoxLayout()
        
        # 文件名
        filename_label = QLabel(self.image_info['filename'])
        filename_label.setStyleSheet("font-weight: bold; color: #333;")
        filename_label.setWordWrap(True)
        
        # 图片信息
        size_info = f"{self.image_info['size'][0]} × {self.image_info['size'][1]}"
        file_size = self.format_file_size(self.image_info['file_size'])
        format_info = self.image_info.get('format', 'Unknown')
        
        info_text = f"尺寸: {size_info}\n大小: {file_size}\n格式: {format_info}"
        if self.image_info.get('has_transparency', False):
            info_text += "\n透明通道: 是"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        
        info_layout.addWidget(filename_label)
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        layout.addWidget(self.thumbnail_label)
        layout.addLayout(info_layout)
        layout.addStretch()
    
    def set_thumbnail(self, pixmap: QPixmap):
        """设置缩略图"""
        if not pixmap.isNull():
            # 调整大小保持宽高比
            scaled_pixmap = pixmap.scaled(78, 78, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            self.thumbnail_label.setText("加载失败")
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


class ImageListWidget(QWidget):
    """图片列表组件"""
    
    # 信号定义
    image_selected = Signal(int)  # 图片被选中
    images_dropped = Signal(list)  # 文件被拖放
    
    def __init__(self):
        super().__init__()
        self.file_manager = FileManager()
        self.thumbnail_loader = None
        self.init_ui()
        self.setup_drag_drop()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题和控制按钮
        header_layout = QHBoxLayout()
        
        title_label = QLabel("图片列表")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        
        # 创建计数信息的垂直布局
        count_widget = QWidget()
        count_layout = QVBoxLayout(count_widget)
        count_layout.setContentsMargins(0, 0, 0, 0)
        count_layout.setSpacing(0)
        
        self.total_count_label = QLabel("0 张图片")
        self.total_count_label.setStyleSheet("color: #666; font-size: 12px;")
        self.total_count_label.setAlignment(Qt.AlignRight)
        
        self.selection_count_label = QLabel("未选中图片")
        self.selection_count_label.setStyleSheet("color: #999; font-size: 11px;")
        self.selection_count_label.setAlignment(Qt.AlignRight)
        
        count_layout.addWidget(self.total_count_label)
        count_layout.addWidget(self.selection_count_label)
        
        # 选择控制按钮
        select_all_btn = QPushButton("全选")
        select_all_btn.setFixedSize(50, 24)
        select_all_btn.clicked.connect(self.select_all_images)
        
        clear_selection_btn = QPushButton("取消选择")
        clear_selection_btn.setFixedSize(70, 24)
        clear_selection_btn.clicked.connect(self.clear_selection)
        
        self.clear_button = QPushButton("清空")
        self.clear_button.setFixedSize(50, 24)
        self.clear_button.clicked.connect(self.clear_all_images)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(count_widget)
        header_layout.addWidget(select_all_btn)
        header_layout.addWidget(clear_selection_btn)
        header_layout.addWidget(self.clear_button)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setAlternatingRowColors(False)  # 关闭交替行颜色
        self.image_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 2px;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 4px;
            }
            QListWidget::item:hover:!selected {
                background-color: #f5f5f5;
            }
        """)
        # 设置选择模式为扩展选择（支持多选）
        from PySide6.QtWidgets import QAbstractItemView
        self.image_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.image_list.itemClicked.connect(self.on_item_clicked)
        self.image_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.image_list)
        layout.addWidget(self.progress_bar)
    
    def setup_drag_drop(self):
        """设置拖放功能"""
        self.setAcceptDrops(True)
        self.image_list.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.exists(file_path):
                files.append(file_path)
        
        if files:
            self.images_dropped.emit(files)
        
        event.acceptProposedAction()
    
    def add_images(self, file_paths: list):
        """添加图片到列表"""
        # 添加文件到文件管理器
        success_count = 0
        for file_path in file_paths:
            if os.path.isdir(file_path):
                # 如果是文件夹，添加文件夹中的图片
                success_count += self.file_manager.add_folder(file_path)
            else:
                # 如果是文件，直接添加
                if self.file_manager.add_single_image(file_path):
                    success_count += 1
        
        if success_count > 0:
            self.refresh_list()
            QMessageBox.information(self, "添加成功", f"成功添加 {success_count} 张图片")
        else:
            QMessageBox.warning(self, "添加失败", "没有找到支持的图片格式")
    
    def refresh_list(self):
        """刷新图片列表"""
        self.image_list.clear()
        images = self.file_manager.get_image_list()
        
        # 更新数量显示
        self.update_count_label()
        
        # 添加列表项
        for i, img_info in enumerate(images):
            item = QListWidgetItem()
            item.setSizeHint(QSize(300, 90))
            
            item_widget = ImageListItem(img_info, i)
            
            self.image_list.addItem(item)
            self.image_list.setItemWidget(item, item_widget)
        
        # 开始加载缩略图
        self.load_thumbnails()
    
    def load_thumbnails(self):
        """加载缩略图"""
        if self.thumbnail_loader and self.thumbnail_loader.isRunning():
            self.thumbnail_loader.stop()
            self.thumbnail_loader.wait()
        
        if self.file_manager.get_image_count() == 0:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(self.file_manager.get_image_count())
        
        self.thumbnail_loader = ThumbnailLoader(self.file_manager)
        self.thumbnail_loader.thumbnail_ready.connect(self.on_thumbnail_ready)
        self.thumbnail_loader.progress_updated.connect(self.on_progress_updated)
        self.thumbnail_loader.finished.connect(lambda: self.progress_bar.setVisible(False))
        self.thumbnail_loader.start()
    
    def on_thumbnail_ready(self, index: int, pixmap: QPixmap):
        """缩略图准备完成"""
        item = self.image_list.item(index)
        if item:
            item_widget = self.image_list.itemWidget(item)
            if isinstance(item_widget, ImageListItem):
                item_widget.set_thumbnail(pixmap)
    
    def on_progress_updated(self, current: int, total: int):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"加载缩略图 {current}/{total}")
    
    def on_item_clicked(self, item: QListWidgetItem):
        """列表项被点击"""
        index = self.image_list.row(item)
        self.image_selected.emit(index)
    
    def on_selection_changed(self):
        """选择状态改变"""
        # 同步选中状态到文件管理器
        self.file_manager.clear_selection()
        for item in self.image_list.selectedItems():
            index = self.image_list.row(item)
            self.file_manager.set_selected(index, True)
        
        # 更新计数显示
        self.update_count_label()
        
        # 如果有选中项，预览第一个选中的图片
        selected_items = self.image_list.selectedItems()
        if selected_items:
            first_selected_index = self.image_list.row(selected_items[0])
            self.image_selected.emit(first_selected_index)
    
    def clear_all_images(self):
        """清空所有图片"""
        if self.file_manager.get_image_count() == 0:
            return
        
        reply = QMessageBox.question(self, "确认清空", "确定要清空所有图片吗？",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.thumbnail_loader and self.thumbnail_loader.isRunning():
                self.thumbnail_loader.stop()
                self.thumbnail_loader.wait()
            
            self.file_manager.clear_all_images()
            self.refresh_list()
    
    def select_all_images(self):
        """全选所有图片"""
        self.image_list.selectAll()
    
    def clear_selection(self):
        """清空选择"""
        self.image_list.clearSelection()
        self.file_manager.clear_selection()
        self.update_count_label()
    
    def update_count_label(self):
        """更新计数标签"""
        total_count = self.file_manager.get_image_count()
        selected_count = self.file_manager.get_selected_count()
        
        # 更新总数标签
        self.total_count_label.setText(f"{total_count} 张图片")
        
        # 更新选中状态标签
        if selected_count > 0:
            self.selection_count_label.setText(f"已选 {selected_count} 张")
            self.selection_count_label.setStyleSheet("color: #2196f3; font-size: 11px;")  # 蓝色表示有选中
        else:
            self.selection_count_label.setText("未选中图片")
            self.selection_count_label.setStyleSheet("color: #999; font-size: 11px;")  # 灰色表示未选中
    
    def get_file_manager(self) -> FileManager:
        """获取文件管理器"""
        return self.file_manager
    
    def get_selected_index(self) -> int:
        """获取当前选中的图片索引"""
        current_row = self.image_list.currentRow()
        return current_row if current_row >= 0 else 0
