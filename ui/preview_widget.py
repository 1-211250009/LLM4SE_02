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
from PySide6.QtCore import Qt, Signal, QSize, QRect, QPoint
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QMouseEvent, QPen
from PIL import Image, ImageDraw, ImageFont

from core.image_processor import ImageProcessor
from core.watermark import TextWatermark, ImageWatermark


class PreviewLabel(QLabel):
    """可缩放的预览标签，支持水印拖拽"""
    
    # 信号定义
    watermark_position_changed = Signal(float, float)  # 水印位置变更信号 (相对位置)
    
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
        
        # 拖拽相关属性
        self.current_watermark = None
        self.watermark_type = 'text'
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self.show_drag_frame = False  # 是否显示拖拽框
        self.watermark_rect = QRect()  # 水印区域
    
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
    
    def set_watermark(self, watermark, watermark_type='text'):
        """设置水印"""
        self.current_watermark = watermark
        self.watermark_type = watermark_type
        self.update_watermark_rect()
        self.update()
    
    def get_image_display_rect(self):
        """获取图像在标签中的显示区域"""
        if not self.original_pixmap:
            return QRect()
        
        widget_size = self.size()
        pixmap_size = self.original_pixmap.size()
        
        # 计算缩放后的尺寸
        scaled_pixmap = self.original_pixmap.scaled(
            widget_size * 0.9,  # 留一些边距
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # 计算居中位置
        x = (widget_size.width() - scaled_pixmap.width()) // 2
        y = (widget_size.height() - scaled_pixmap.height()) // 2
        
        return QRect(x, y, scaled_pixmap.width(), scaled_pixmap.height())
    
    def get_actual_watermark_bounds(self, watermark, watermark_type, scale_ratio):
        """通过实际渲染获取水印的精确边界 - 基于像素点分析"""
        try:
            if watermark_type != 'text':
                # 图片水印暂时使用原来的逻辑
                return 100, 100
            
            # 创建较小的临时图像（500x500足够测量文字）
            temp_size = 500
            temp_img = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
            
            # 创建临时水印对象
            temp_watermark = watermark.__class__()
            temp_watermark.__dict__.update(watermark.__dict__)
            
            # 临时调整字体大小以匹配显示缩放
            original_font_size = watermark.font_size
            temp_watermark.font_size = int(original_font_size * scale_ratio)
            
            # 设置水印在图像中心位置
            temp_watermark.position = (0.5, 0.5)
            
            # 渲染水印
            watermarked = temp_watermark.apply_to_image(temp_img)
            
            # 恢复原始字体大小
            watermark.font_size = original_font_size
            
            # 获取边界框 - PIL的getbbox()直接返回非透明区域的边界
            bbox = watermarked.getbbox()
            if bbox is None:
                # 如果没有找到内容，使用文本估算
                text = getattr(watermark, 'text', 'Sample')
                scaled_font_size = int(original_font_size * scale_ratio)
                return len(text) * scaled_font_size // 2, scaled_font_size
            
            left, top, right, bottom = bbox
            actual_width = right - left
            actual_height = bottom - top
            
            # 添加小量缓冲以确保完整包含
            actual_width += 4  # 左右各2像素缓冲
            actual_height += 4  # 上下各2像素缓冲
            
            return actual_width, actual_height
            
        except Exception as e:
            print(f"获取水印边界失败: {e}")
            # 回退到简单估算
            text = getattr(watermark, 'text', 'Sample')
            scaled_font_size = int(getattr(watermark, 'font_size', 32) * scale_ratio)
            return len(text) * scaled_font_size // 2, scaled_font_size
    
    def get_watermark_display_size(self):
        """获取水印在显示区域中的尺寸"""
        if not self.current_watermark:
            return 50, 50
        
        image_rect = self.get_image_display_rect()
        if image_rect.isEmpty():
            return 50, 50
        
        if self.watermark_type == 'text':
            if self.original_pixmap:
                scale_ratio = image_rect.width() / self.original_pixmap.width()
                
                # 使用实际渲染边界获取精确尺寸
                watermark_width, watermark_height = self.get_actual_watermark_bounds(
                    self.current_watermark, self.watermark_type, scale_ratio
                )
                
                watermark_width = max(watermark_width, 30)
                watermark_height = max(watermark_height, 20)
            else:
                watermark_width = 80
                watermark_height = 30
        else:
            if hasattr(self.current_watermark, 'watermark_image') and self.current_watermark.watermark_image:
                original_w = self.current_watermark.watermark_image.width
                original_h = self.current_watermark.watermark_image.height
                scale = getattr(self.current_watermark, 'scale', 1.0)
                
                if self.original_pixmap:
                    display_scale = image_rect.width() / self.original_pixmap.width()
                    watermark_width = int(original_w * scale * display_scale)
                    watermark_height = int(original_h * scale * display_scale)
                else:
                    watermark_width = int(original_w * scale * 0.3)
                    watermark_height = int(original_h * scale * 0.3)
                
                watermark_width = max(watermark_width, 30)
                watermark_height = max(watermark_height, 30)
            else:
                watermark_width = 50
                watermark_height = 50
        
        return watermark_width, watermark_height
    
    def update_watermark_rect(self):
        """更新水印区域"""
        if not self.current_watermark:
            self.watermark_rect = QRect()
            return
        
        image_rect = self.get_image_display_rect()
        if image_rect.isEmpty():
            self.watermark_rect = QRect()
            return
        
        # 获取水印相对位置和尺寸
        rel_x, rel_y = self.current_watermark.position
        watermark_width, watermark_height = self.get_watermark_display_size()
        
        # 按照水印渲染逻辑计算边框位置
        # 模拟 x = int((img_width - text_width) * self.position[0])
        # 在显示区域中：x = image_rect.x() + int((image_rect.width() - watermark_width) * rel_x)
        watermark_x = image_rect.x() + int((image_rect.width() - watermark_width) * rel_x)
        watermark_y = image_rect.y() + int((image_rect.height() - watermark_height) * rel_y)
        
        self.watermark_rect = QRect(watermark_x, watermark_y, watermark_width, watermark_height)
    
    def screen_pos_to_relative(self, screen_pos):
        """将屏幕坐标转换为相对位置（按照水印逻辑）"""
        image_rect = self.get_image_display_rect()
        if image_rect.isEmpty() or not self.current_watermark:
            return 0.5, 0.5
        
        # 获取水印显示尺寸
        watermark_width, watermark_height = self.get_watermark_display_size()
        
        # 反向计算相对位置
        # 从 x = image_rect.x() + int((image_rect.width() - watermark_width) * rel_x)
        # 得到 rel_x = (x - image_rect.x()) / (image_rect.width() - watermark_width)
        screen_x_offset = screen_pos.x() - image_rect.x()
        screen_y_offset = screen_pos.y() - image_rect.y()
        
        if image_rect.width() - watermark_width > 0:
            rel_x = screen_x_offset / (image_rect.width() - watermark_width)
        else:
            rel_x = 0.5
            
        if image_rect.height() - watermark_height > 0:
            rel_y = screen_y_offset / (image_rect.height() - watermark_height)
        else:
            rel_y = 0.5
        
        # 限制在[0,1]范围内
        rel_x = max(0.0, min(1.0, rel_x))
        rel_y = max(0.0, min(1.0, rel_y))
        
        return rel_x, rel_y
    
    def paintEvent(self, event):
        """绘制事件 - 添加拖拽框"""
        super().paintEvent(event)
        
        # 绘制拖拽框
        if self.show_drag_frame and not self.watermark_rect.isEmpty():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 设置透明虚线（保留拖拽功能但不显示边框）
            pen = QPen(QColor(255, 255, 255, 0), 2, Qt.DashLine)
            painter.setPen(pen)
            
            # 绘制外框
            painter.drawRect(self.watermark_rect)
            
            painter.end()
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton and self.current_watermark:
            self.update_watermark_rect()
            
            # 检查是否点击在水印区域内
            if self.watermark_rect.contains(event.position().toPoint()):
                self.is_dragging = True
                self.show_drag_frame = True
                self.drag_start_pos = event.position().toPoint()
                self.setCursor(Qt.ClosedHandCursor)
                self.update()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.is_dragging and self.current_watermark:
            # 计算鼠标移动偏移量
            mouse_offset = event.position().toPoint() - self.drag_start_pos
            
            # 计算边框新的左上角位置（当前边框位置 + 偏移量）
            if not self.watermark_rect.isEmpty():
                new_frame_x = self.watermark_rect.x() + mouse_offset.x()
                new_frame_y = self.watermark_rect.y() + mouse_offset.y()
                
                # 转换为相对位置
                rel_x, rel_y = self.screen_pos_to_relative(QPoint(new_frame_x, new_frame_y))
                
                # 更新拖拽起点，避免累积偏移
                self.drag_start_pos = event.position().toPoint()
                
                # 更新水印位置
                self.current_watermark.set_position(rel_x, rel_y)
                
                # 更新拖拽框位置
                self.update_watermark_rect()
                
                # 发送位置变更信号
                self.watermark_position_changed.emit(rel_x, rel_y)
                
                self.update()
        elif self.current_watermark:
            # 检查鼠标是否悬停在水印区域
            self.update_watermark_rect()
            if self.watermark_rect.contains(event.position().toPoint()):
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.show_drag_frame = False
            self.setCursor(Qt.ArrowCursor)
            self.update()
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        if self.original_pixmap:
            self.update_display()
            self.update_watermark_rect()


class PreviewWidget(QWidget):
    """图片预览组件"""
    
    # 信号定义
    watermark_position_changed = Signal(float, float)  # 水印位置变更信号
    
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
        
        # 连接PreviewLabel的拖拽信号
        self.preview_label.watermark_position_changed.connect(self.on_watermark_position_changed)
    
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
            
            # 显示图片
            self.preview_label.set_image(pixmap)
            
            # 应用水印到显示图像（如果有）
            if self.current_watermark:
                # 获取显示图像的实际尺寸
                display_rect = self.preview_label.get_image_display_rect()
                if not display_rect.isEmpty():
                    # 创建与显示区域大小一致的图像用于水印渲染
                    display_image = image.resize((display_rect.width(), display_rect.height()), Image.LANCZOS)
                    
                    # 创建临时水印对象，调整字体大小以匹配显示缩放
                    temp_watermark = self.current_watermark.__class__()
                    temp_watermark.__dict__.update(self.current_watermark.__dict__)
                    
                    # 计算缩放比例并调整字体大小
                    if hasattr(self.current_watermark, 'font_size'):
                        scale_ratio = display_rect.width() / image.width
                        temp_watermark.font_size = int(self.current_watermark.font_size * scale_ratio)
                    
                    watermarked_display_image = temp_watermark.apply_to_image(display_image)
                    watermarked_pixmap = self.pil_to_qpixmap(watermarked_display_image)
                    
                    # 更新显示
                    self.preview_label.set_image(watermarked_pixmap)
            
            # 更新信息显示
            filename = os.path.basename(image_path)
            size_info = f"{image.size[0]} × {image.size[1]}"
            watermark_info = " [已添加水印]" if self.current_watermark else ""
            self.image_info_label.setText(f"{filename} - {size_info}{watermark_info}")
            
        except FileNotFoundError:
            self.show_error(f"错误: 文件不存在 - {image_path}")
        except PermissionError:
            self.show_error(f"错误: 没有权限访问文件 - {image_path}")
        except Exception as e:
            error_msg = str(e)
            if "cannot identify image file" in error_msg.lower():
                self.show_error(f"错误: 不支持的图片格式 - {os.path.basename(image_path)}")
            elif "truncated" in error_msg.lower():
                self.show_error(f"错误: 图片文件损坏 - {os.path.basename(image_path)}")
            else:
                self.show_error(f"错误: 加载图片失败 - {os.path.basename(image_path)}: {error_msg}")
    
    def _clean_png_for_qt(self, pil_image):
        """清理PNG图片以避免Qt的ICC颜色空间警告"""
        if pil_image.mode == 'RGBA':
            # 移除ICC profile以避免Qt警告
            clean_image = Image.new('RGBA', pil_image.size, (0, 0, 0, 0))
            clean_image.paste(pil_image, (0, 0))
            return clean_image
        return pil_image
    
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
            
            # 清理图片以避免Qt警告
            clean_image = self._clean_png_for_qt(pil_image)
            
            # 根据模式选择保存格式
            if clean_image.mode == 'RGBA':
                # 对于RGBA模式，保存为PNG以保持透明通道
                clean_image.save(buffer, format='PNG', optimize=True)
            elif clean_image.mode in ('LA', 'P'):
                # 灰度+透明度或调色板模式，转换为RGBA后保存为PNG
                if clean_image.mode != 'RGBA':
                    clean_image = clean_image.convert('RGBA')
                clean_image.save(buffer, format='PNG', optimize=True)
            else:
                # 其他模式转换为RGB并保存为JPEG
                if clean_image.mode != 'RGB':
                    clean_image = clean_image.convert('RGB')
                clean_image.save(buffer, format='JPEG', quality=95)
            
            buffer.seek(0)
            
            # 从字节流创建QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            return pixmap
            
        except Exception as e:
            error_msg = str(e)
            if "insufficient memory" in error_msg.lower():
                print(f"错误: 内存不足，无法转换图片格式")
            else:
                print(f"错误: 转换图片格式失败: {error_msg}")
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
    
    def on_watermark_position_changed(self, rel_x, rel_y):
        """处理水印位置变更"""
        # 转发信号给主窗口
        self.watermark_position_changed.emit(rel_x, rel_y)
    
    def set_watermark(self, watermark, watermark_type: str = 'text'):
        """设置水印
        
        Args:
            watermark: 水印对象
            watermark_type: 水印类型 ('text' 或 'image')
        """
        self.current_watermark = watermark
        self.watermark_type = watermark_type
        
        # 同步到PreviewLabel
        self.preview_label.set_watermark(watermark, watermark_type)
        
        # 刷新预览
        if self.current_image_path:
            self.load_image(self.current_image_path)
        else:
            # 即使没有图片，也要更新预览标签以正确显示水印框
            self.preview_label.update_watermark_rect()
            self.preview_label.update()
    
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
