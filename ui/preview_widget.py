#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Preview Widget
图片预览组件
"""

import os
from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor

from core.image_processor import ImageProcessor
from core.watermark import TextWatermark


class PreviewLabel(QLabel):
    """可缩放的预览标签"""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                background-color: #f9f9f9;
                border-radius: 8px;
            }
        """)
        self.original_pixmap = None
        self.scale_factor = 1.0
    
    def set_image(self, pixmap: QPixmap):
        """设置图片"""
        self.original_pixmap = pixmap
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        if self.original_pixmap:
            # 计算合适的显示大小
            widget_size = self.size()
            pixmap_size = self.original_pixmap.size()
            
            # 保持宽高比缩放
            scaled_pixmap = self.original_pixmap.scaled(
                widget_size * 0.9,  # 留一些边距
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.setPixmap(scaled_pixmap)
            self.scale_factor = scaled_pixmap.width() / pixmap_size.width()
        else:
            self.clear()
            self.setText("请选择图片进行预览")
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        if self.original_pixmap:
            self.update_display()


class PreviewWidget(QWidget):
    """图片预览组件"""
    
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.current_image_path = None
        self.current_image = None
        self.current_watermark = None
        self.watermark_type = 'text'
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        title_label = QLabel("预览")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        
        self.image_info_label = QLabel("未选择图片")
        self.image_info_label.setStyleSheet("color: #666; font-size: 12px;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.image_info_label)
        
        # 预览区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # 预览标签
        self.preview_label = PreviewLabel()
        self.scroll_area.setWidget(self.preview_label)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.scroll_area)
    
    def load_image(self, image_path: str):
        """加载图片进行预览
        
        Args:
            image_path: 图片文件路径
        """
        try:
            if not os.path.exists(image_path):
                self.show_error("文件不存在")
                return
            
            # 加载图片
            image = self.image_processor.load_image(image_path)
            if image is None:
                self.show_error("无法加载图片")
                return
            
            self.current_image_path = image_path
            self.current_image = image
            
            # 转换为QPixmap
            pixmap = self.pil_to_qpixmap(image)
            if pixmap.isNull():
                self.show_error("图片格式不支持")
                return
            
            # 应用水印（如果有）
            if self.current_watermark and self.watermark_type == 'text':
                image = self.current_watermark.apply_to_image(image)
                pixmap = self.pil_to_qpixmap(image)
            
            # 显示图片
            self.preview_label.set_image(pixmap)
            
            # 更新信息显示
            filename = os.path.basename(image_path)
            size_info = f"{image.size[0]} × {image.size[1]}"
            watermark_info = " [已添加水印]" if self.current_watermark else ""
            self.image_info_label.setText(f"{filename} - {size_info}{watermark_info}")
            
        except Exception as e:
            self.show_error(f"加载图片失败: {e}")
    
    def pil_to_qpixmap(self, pil_image) -> QPixmap:
        """将PIL图片转换为QPixmap
        
        Args:
            pil_image: PIL图片对象
            
        Returns:
            QPixmap: Qt图片对象
        """
        try:
            from PySide6.QtGui import QImage
            import io
            
            # 使用临时字节流的方法，这样更可靠
            buffer = io.BytesIO()
            
            # 根据模式选择保存格式
            if pil_image.mode == 'RGBA':
                pil_image.save(buffer, format='PNG')
            else:
                # 转换为RGB并保存为JPEG
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                pil_image.save(buffer, format='JPEG', quality=95)
            
            buffer.seek(0)
            
            # 从字节流创建QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            return pixmap
            
        except Exception as e:
            print(f"转换图片格式失败: {e}")
            return QPixmap()
    
    def show_error(self, message: str):
        """显示错误信息
        
        Args:
            message: 错误信息
        """
        self.preview_label.clear()
        self.preview_label.setText(f"错误: {message}")
        self.image_info_label.setText("加载失败")
        self.current_image_path = None
        self.current_image = None
    
    def clear_preview(self):
        """清空预览"""
        self.preview_label.clear()
        self.preview_label.setText("请选择图片进行预览")
        self.image_info_label.setText("未选择图片")
        self.current_image_path = None
        self.current_image = None
    
    def get_current_image_path(self) -> Optional[str]:
        """获取当前预览的图片路径
        
        Returns:
            str or None: 当前图片路径
        """
        return self.current_image_path
    
    def get_current_image(self):
        """获取当前预览的PIL图片对象
        
        Returns:
            PIL.Image or None: 当前图片对象
        """
        return self.current_image
    
    def set_watermark(self, watermark, watermark_type: str = 'text'):
        """设置水印
        
        Args:
            watermark: 水印对象
            watermark_type: 水印类型 ('text' 或 'image')
        """
        self.current_watermark = watermark
        self.watermark_type = watermark_type
        
        # 刷新预览
        if self.current_image_path:
            self.load_image(self.current_image_path)
    
    def clear_watermark(self):
        """清除水印"""
        self.current_watermark = None
        
        # 刷新预览
        if self.current_image_path:
            self.load_image(self.current_image_path)
    
    def get_watermarked_image(self):
        """获取添加水印后的图片
        
        Returns:
            PIL.Image or None: 添加水印后的图片
        """
        if not self.current_image:
            return None
        
        if self.current_watermark and self.watermark_type == 'text':
            return self.current_watermark.apply_to_image(self.current_image)
        else:
            return self.current_image.copy()
