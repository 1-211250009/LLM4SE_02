#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Watermark Core
水印核心模块
"""

from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import os


class TextWatermark:
    """文本水印类"""
    
    def __init__(self):
        """初始化文本水印"""
        self.text = "Photo Watermark"
        self.font_size = 24
        self.font_color = (255, 255, 255, 180)  # RGBA: 白色，透明度180
        self.position = (0.5, 0.5)  # 相对位置 (0.0-1.0)
        self.rotation = 0  # 旋转角度
        
    def set_text(self, text: str):
        """设置水印文本
        
        Args:
            text: 水印文本
        """
        self.text = text if text else "Photo Watermark"
    
    def set_font_size(self, size: int):
        """设置字体大小
        
        Args:
            size: 字体大小 (10-200)
        """
        self.font_size = max(10, min(200, size))
    
    def set_transparency(self, transparency: int):
        """设置透明度
        
        Args:
            transparency: 透明度 (0-100), 0为完全透明，100为完全不透明
        """
        alpha = int(255 * transparency / 100)
        self.font_color = (*self.font_color[:3], alpha)
    
    def set_color(self, color: Tuple[int, int, int]):
        """设置字体颜色
        
        Args:
            color: RGB颜色元组
        """
        self.font_color = (*color, self.font_color[3])
    
    def set_position(self, x: float, y: float):
        """设置水印位置
        
        Args:
            x: 水平位置 (0.0-1.0)
            y: 垂直位置 (0.0-1.0)
        """
        self.position = (max(0.0, min(1.0, x)), max(0.0, min(1.0, y)))
    
    def set_rotation(self, angle: float):
        """设置旋转角度
        
        Args:
            angle: 旋转角度（度）
        """
        self.rotation = angle % 360
    
    def get_font(self) -> ImageFont.ImageFont:
        """获取字体对象
        
        Returns:
            ImageFont.ImageFont: 字体对象
        """
        try:
            # 尝试使用系统默认字体
            font = ImageFont.truetype("Arial.ttf", self.font_size)
        except (OSError, IOError):
            try:
                # macOS 系统字体
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", self.font_size)
            except (OSError, IOError):
                try:
                    # 备用字体
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size)
                except (OSError, IOError):
                    # 使用默认字体
                    font = ImageFont.load_default()
        
        return font
    
    def calculate_text_size(self, font: ImageFont.ImageFont) -> Tuple[int, int]:
        """计算文本尺寸
        
        Args:
            font: 字体对象
            
        Returns:
            Tuple[int, int]: 文本宽度和高度
        """
        # 创建临时图像来测量文本尺寸
        temp_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        
        # 获取文本边界框
        bbox = draw.textbbox((0, 0), self.text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        return width, height
    
    def apply_to_image(self, image: Image.Image) -> Image.Image:
        """将文本水印应用到图像
        
        Args:
            image: 原始图像
            
        Returns:
            Image.Image: 添加水印后的图像
        """
        if not self.text:
            return image.copy()
        
        # 创建图像副本
        watermarked_image = image.copy()
        
        # 确保图像为RGBA模式以支持透明度
        if watermarked_image.mode != 'RGBA':
            watermarked_image = watermarked_image.convert('RGBA')
        
        # 获取字体
        font = self.get_font()
        
        # 计算文本尺寸
        text_width, text_height = self.calculate_text_size(font)
        
        # 计算水印位置
        img_width, img_height = watermarked_image.size
        x = int((img_width - text_width) * self.position[0])
        y = int((img_height - text_height) * self.position[1])
        
        # 如果需要旋转，创建旋转的文本图像
        if self.rotation != 0:
            # 创建文本图像
            text_img = Image.new('RGBA', (text_width * 2, text_height * 2), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            
            # 在文本图像中心绘制文本
            text_x = (text_img.width - text_width) // 2
            text_y = (text_img.height - text_height) // 2
            text_draw.text((text_x, text_y), self.text, font=font, fill=self.font_color)
            
            # 旋转文本图像
            rotated_text = text_img.rotate(self.rotation, expand=False)
            
            # 计算旋转后的位置调整
            rot_width, rot_height = rotated_text.size
            adj_x = x - (rot_width - text_width) // 2
            adj_y = y - (rot_height - text_height) // 2
            
            # 粘贴旋转后的文本
            watermarked_image.paste(rotated_text, (adj_x, adj_y), rotated_text)
        else:
            # 直接在图像上绘制文本
            draw = ImageDraw.Draw(watermarked_image)
            draw.text((x, y), self.text, font=font, fill=self.font_color)
        
        return watermarked_image
    
    def get_preset_positions(self) -> dict:
        """获取预设位置
        
        Returns:
            dict: 预设位置字典
        """
        return {
            "左上角": (0.05, 0.05),
            "上中": (0.5, 0.05),
            "右上角": (0.95, 0.05),
            "左中": (0.05, 0.5),
            "正中心": (0.5, 0.5),
            "右中": (0.95, 0.5),
            "左下角": (0.05, 0.95),
            "下中": (0.5, 0.95),
            "右下角": (0.95, 0.95)
        }
    
    def set_preset_position(self, position_name: str):
        """设置预设位置
        
        Args:
            position_name: 位置名称
        """
        positions = self.get_preset_positions()
        if position_name in positions:
            self.position = positions[position_name]


class ImageWatermark:
    """图片水印类（为后续功能预留）"""
    
    def __init__(self):
        """初始化图片水印"""
        self.watermark_image = None
        self.position = (0.5, 0.5)
        self.scale = 1.0
        self.transparency = 0.8
        
    def load_watermark_image(self, image_path: str) -> bool:
        """加载水印图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            bool: 是否加载成功
        """
        try:
            self.watermark_image = Image.open(image_path)
            if self.watermark_image.mode != 'RGBA':
                self.watermark_image = self.watermark_image.convert('RGBA')
            return True
        except Exception as e:
            print(f"加载水印图片失败: {e}")
            return False
    
    def apply_to_image(self, image: Image.Image) -> Image.Image:
        """将图片水印应用到图像（预留功能）
        
        Args:
            image: 原始图像
            
        Returns:
            Image.Image: 添加水印后的图像
        """
        # 此功能将在阶段3实现
        return image.copy()
