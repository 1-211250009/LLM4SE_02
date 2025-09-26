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
        # 支持中文的字体优先级列表
        font_paths = [
            # macOS 中文字体
            "/System/Library/Fonts/PingFang.ttc",  # 苹方，支持中文
            "/System/Library/Fonts/STHeiti Light.ttc",  # 黑体
            "/System/Library/Fonts/STSong.ttc",  # 宋体
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 冬青黑体简体中文
            
            # 英文字体
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            
            # Windows 字体（以防在其他系统运行）
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttf",  # 宋体
            "C:/Windows/Fonts/arial.ttf",
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, self.font_size)
                return font
            except (OSError, IOError):
                continue
        
        # 如果所有字体都失败，使用默认字体
        try:
            return ImageFont.load_default()
        except:
            # 如果连默认字体都失败，创建一个简单的字体
            return ImageFont.load_default()
    
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
        
        # 检查透明度，如果完全透明则不绘制
        if self.font_color[3] == 0:
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
        
        # 如果文本尺寸为0，返回原图
        if text_width == 0 or text_height == 0:
            return watermarked_image
        
        # 计算水印位置
        img_width, img_height = watermarked_image.size
        x = int((img_width - text_width) * self.position[0])
        y = int((img_height - text_height) * self.position[1])
        
        # 创建一个单独的透明层来绘制文本
        text_layer = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
        
        # 如果需要旋转，创建旋转的文本图像
        if self.rotation != 0:
            # 创建文本图像，使用更大的画布以容纳旋转
            text_canvas_size = max(text_width, text_height) * 3
            text_img = Image.new('RGBA', (text_canvas_size, text_canvas_size), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            
            # 在文本图像中心绘制文本
            text_x = (text_canvas_size - text_width) // 2
            text_y = (text_canvas_size - text_height) // 2
            text_draw.text((text_x, text_y), self.text, font=font, fill=self.font_color)
            
            # 旋转文本图像
            rotated_text = text_img.rotate(self.rotation, expand=False)
            
            # 计算粘贴位置
            paste_x = x - (text_canvas_size - text_width) // 2
            paste_y = y - (text_canvas_size - text_height) // 2
            
            # 粘贴到文本层
            text_layer.paste(rotated_text, (paste_x, paste_y), rotated_text)
        else:
            # 直接在文本层绘制文本
            draw = ImageDraw.Draw(text_layer)
            draw.text((x, y), self.text, font=font, fill=self.font_color)
        
        # 合并文本层到主图像
        watermarked_image = Image.alpha_composite(watermarked_image, text_layer)
        
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
