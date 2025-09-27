#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Watermark Core
水印核心模块
"""

from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import os
import math


class TextWatermark:
    """文本水印类"""
    
    def __init__(self):
        """初始化文本水印"""
        self.text = "Photo Watermark"
        self.font_size = 60
        self.font_color = (255, 255, 255, 255)  # RGBA: 白色，100%不透明度
        self.position = (0.95, 0.95)  # 相对位置 (0.0-1.0) - 右下角
        self.rotation = 0  # 旋转角度
        
        # 新增高级功能属性
        self.font_family = "默认字体"  # 字体家族
        self.font_bold = False  # 粗体
        self.font_italic = False  # 斜体
        
        # 阴影效果
        self.shadow_enabled = False
        self.shadow_offset = (2, 2)  # 阴影偏移 (x, y)
        self.shadow_color = (0, 0, 0, 128)  # 阴影颜色 RGBA
        self.shadow_blur = 0  # 阴影模糊度
        
        # 描边效果
        self.stroke_enabled = False
        self.stroke_width = 2  # 描边宽度
        self.stroke_color = (0, 0, 0, 255)  # 描边颜色 RGBA
        
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
    
    def set_font_family(self, family: str):
        """设置字体家族
        
        Args:
            family: 字体家族名称
        """
        self.font_family = family
    
    def set_font_style(self, bold: bool = None, italic: bool = None):
        """设置字体样式
        
        Args:
            bold: 是否粗体
            italic: 是否斜体
        """
        if bold is not None:
            self.font_bold = bold
        if italic is not None:
            self.font_italic = italic
    
    def set_shadow(self, enabled: bool, offset: tuple = None, color: tuple = None, blur: int = None):
        """设置阴影效果
        
        Args:
            enabled: 是否启用阴影
            offset: 阴影偏移 (x, y)
            color: 阴影颜色 RGBA
            blur: 阴影模糊度
        """
        self.shadow_enabled = enabled
        if offset is not None:
            self.shadow_offset = offset
        if color is not None:
            self.shadow_color = color
        if blur is not None:
            self.shadow_blur = max(0, blur)
    
    def set_stroke(self, enabled: bool, width: int = None, color: tuple = None):
        """设置描边效果
        
        Args:
            enabled: 是否启用描边
            width: 描边宽度
            color: 描边颜色 RGBA
        """
        self.stroke_enabled = enabled
        if width is not None:
            self.stroke_width = max(0, width)
        if color is not None:
            self.stroke_color = color
    
    def get_font(self) -> ImageFont.ImageFont:
        """获取字体对象
        
        Returns:
            ImageFont.ImageFont: 字体对象
        """
        # 字体映射表，包含基础字体和样式变体，使用多个候选路径确保兼容性
        font_map = {
            "默认字体": {
                "regular": [
                    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/System/Library/Fonts/STHeiti Light.ttc"
                ],
                "bold": [
                    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/System/Library/Fonts/STHeiti Medium.ttc"
                ],
                "italic": [
                    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/System/Library/Fonts/STHeiti Light.ttc"
                ],
                "supports_chinese": True
            },
            "苹方": {
                "regular": [
                    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc"
                ],
                "bold": [
                    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc"
                ],
                "italic": [
                    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc"
                ],
                "supports_chinese": True
            },
            "黑体": {
                "regular": ["/System/Library/Fonts/STHeiti Light.ttc"],
                "bold": ["/System/Library/Fonts/STHeiti Medium.ttc"],
                "italic": ["/System/Library/Fonts/STHeiti Light.ttc"],
                "supports_chinese": True
            },
            "宋体": {
                "regular": ["/System/Library/Fonts/Supplemental/Songti.ttc"],
                "bold": ["/System/Library/Fonts/Supplemental/Songti.ttc"],
                "italic": ["/System/Library/Fonts/Supplemental/Songti.ttc"],
                "supports_chinese": True
            },
            "冬青黑体": {
                "regular": ["/System/Library/Fonts/Hiragino Sans GB.ttc"],
                "bold": ["/System/Library/Fonts/Hiragino Sans GB.ttc"],
                "italic": ["/System/Library/Fonts/Hiragino Sans GB.ttc"],
                "supports_chinese": True
            },
            "Arial": {
                "regular": ["/System/Library/Fonts/Supplemental/Arial.ttf"],
                "bold": ["/System/Library/Fonts/Supplemental/Arial Bold.ttf"], 
                "italic": ["/System/Library/Fonts/Supplemental/Arial Italic.ttf"],
                "supports_chinese": False
            },
            "Helvetica": {
                "regular": ["/System/Library/Fonts/Helvetica.ttc"],
                "bold": ["/System/Library/Fonts/Helvetica.ttc"],
                "italic": ["/System/Library/Fonts/Helvetica.ttc"],
                "supports_chinese": False
            },
            "Times New Roman": {
                "regular": ["/System/Library/Fonts/Times.ttc"],
                "bold": ["/System/Library/Fonts/Times.ttc"],
                "italic": ["/System/Library/Fonts/Times.ttc"],
                "supports_chinese": False
            }
        }
        
        # 获取字体信息
        font_info = font_map.get(self.font_family, font_map["默认字体"])
        
        # 根据样式选择字体路径列表
        font_paths = font_info["regular"]  # 默认使用常规字体
        
        if self.font_bold and self.font_italic:
            # 优先使用粗斜体，如果没有则使用粗体
            font_paths = font_info.get("bold", font_info["regular"])
        elif self.font_bold:
            font_paths = font_info.get("bold", font_info["regular"])
        elif self.font_italic:
            font_paths = font_info.get("italic", font_info["regular"])
        
        # 确保font_paths是一个列表
        if isinstance(font_paths, str):
            font_paths = [font_paths]
        
        # 尝试加载候选字体列表中的字体
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, self.font_size)
                    # 验证字体是否正确加载
                    if hasattr(font, 'getsize') or hasattr(font, 'getbbox'):
                        return font
            except (OSError, IOError):
                continue
        
        # 如果选择的字体列表都失败，尝试常规字体
        regular_paths = font_info["regular"]
        if isinstance(regular_paths, str):
            regular_paths = [regular_paths]
        
        for font_path in regular_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, self.font_size)
                    # 验证字体是否正确加载
                    if hasattr(font, 'getsize') or hasattr(font, 'getbbox'):
                        return font
            except (OSError, IOError):
                continue
        
        # 如果所有字体都失败，尝试系统默认字体
        default_fonts = [
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 最可靠的中文字体
            "/System/Library/Fonts/STHeiti Light.ttc",     # 备用中文字体
            "/System/Library/Fonts/Supplemental/Arial.ttf", # 英文字体
            "/System/Library/Fonts/Helvetica.ttc",        # 系统默认英文字体
            "/System/Library/Fonts/Supplemental/Songti.ttc" # 宋体
        ]
        
        for default_font in default_fonts:
            try:
                font = ImageFont.truetype(default_font, self.font_size)
                # 验证字体是否正确加载
                if hasattr(font, 'getsize') or hasattr(font, 'getbbox'):
                    return font
            except (OSError, IOError):
                continue
        
        # 最后回退到PIL默认字体（但这个字体大小不可调）
        try:
            return ImageFont.load_default()
        except:
            # 如果连默认字体都失败，创建一个简单的字体
            return ImageFont.load_default()
    
    def get_available_fonts(self, text_contains_chinese: bool = None) -> list:
        """获取可用字体列表
        
        Args:
            text_contains_chinese: 是否包含中文，如果为None则检查当前文本
            
        Returns:
            list: 可用字体名称列表
        """
        # 字体映射表（与get_font中的保持一致）
        font_map = {
            "默认字体": {"supports_chinese": True},
            "苹方": {"supports_chinese": True},
            "黑体": {"supports_chinese": True},
            "宋体": {"supports_chinese": True},
            "Arial": {"supports_chinese": False},
            "Helvetica": {"supports_chinese": False},
            "Times New Roman": {"supports_chinese": False}
        }
        
        # 检查是否包含中文
        if text_contains_chinese is None:
            text_contains_chinese = self._contains_chinese(self.text)
        
        # 如果包含中文，只返回支持中文的字体
        if text_contains_chinese:
            fonts = [name for name, info in font_map.items() if info["supports_chinese"]]
        else:
            fonts = list(font_map.keys())
        
        return fonts
    
    def _contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文字符
        
        Args:
            text: 要检查的文本
            
        Returns:
            bool: 是否包含中文字符
        """
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def _calculate_font_extra_height(self, font: ImageFont.ImageFont, text_height: int) -> int:
        """根据字体特性自适应计算额外高度
        
        Args:
            font: 字体对象
            text_height: 文本基础高度
            
        Returns:
            int: 额外需要的高度
        """
        # 测试包含descender的字符来检测字体的下降部分
        test_chars = "gjpqy"
        
        try:
            # 创建临时图像来测量descender高度
            temp_img = Image.new('RGBA', (1, 1))
            draw = ImageDraw.Draw(temp_img)
            
            # 测量普通字符（如'A'）的高度
            normal_bbox = draw.textbbox((0, 0), "A", font=font)
            normal_height = normal_bbox[3] - normal_bbox[1]
            
            # 测量带descender字符的高度
            descender_bbox = draw.textbbox((0, 0), test_chars, font=font)
            descender_height = descender_bbox[3] - descender_bbox[1]
            
            # 计算descender额外高度
            descender_extra = max(0, descender_height - normal_height)
            
            # 如果字体有明显的descender，使用较小的百分比；否则使用较大的百分比
            if descender_extra > normal_height * 0.1:  # descender超过正常高度的10%
                # 字体有明显descender，使用30%额外空间
                extra_ratio = 0.3
            else:
                # 字体descender较小或没有，使用50%额外空间以防万一
                extra_ratio = 0.5
            
            # 还要考虑中文字体通常需要更多空间
            if self._contains_chinese(self.text):
                extra_ratio += 0.1  # 中文字体额外增加10%
            
            # 针对特定字体的微调
            font_name = getattr(font, 'path', '') or str(font)
            font_name_lower = font_name.lower()
            
            # 检查是否是默认字体（PIL的load_default）
            is_default_font = (hasattr(font, '_name') and font._name == 'DEFAULT') or 'default' in font_name_lower
            
            # 默认字体和苹方需要额外增加
            if (is_default_font or
                'pingfang' in font_name_lower or 
                '苹方' in font_name_lower or
                'arial' in font_name_lower or
                '宋体' in font_name_lower):
                extra_ratio += 0.2
            
            # 黑体需要削减
            elif ('heiti' in font_name_lower or 
                  '黑体' in font_name_lower or
                  'simhei' in font_name_lower or
                  'microsoft yahei' in font_name_lower):
                extra_ratio -= 0.4
                
            return int(text_height * max(0.1, extra_ratio))  # 确保至少有10%的额外空间
            
        except Exception:
            # 如果测量失败，使用默认的50%
            return int(text_height * 0.5)
    
    def calculate_text_size(self, font: ImageFont.ImageFont) -> Tuple[int, int]:
        """计算文本尺寸（考虑所有样式效果）
        
        Args:
            font: 字体对象
            
        Returns:
            Tuple[int, int]: 文本宽度和高度
        """
        # 创建临时图像来测量文本尺寸
        temp_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        
        # 获取基础文本边界框
        bbox = draw.textbbox((0, 0), self.text, font=font)
        base_width = bbox[2] - bbox[0]
        base_height = bbox[3] - bbox[1]
        
        # 根据样式调整尺寸
        if self.font_bold and self.font_italic:
            # 粗斜体：需要考虑斜体变换和粗体扩展
            slant_factor = 0.15
            max_offset = int(base_height * slant_factor)
            extra_height = max(30, int(base_height * 0.8))
            bold_extra = 2
            
            width = base_width + max_offset + bold_extra + 10
            height = base_height + extra_height + bold_extra
        elif self.font_bold:
            # 粗体：增加2像素的额外尺寸
            width = base_width + 2
            height = base_height + 2
        elif self.font_italic:
            # 斜体：需要考虑斜体变换
            slant_factor = 0.15
            max_offset = int(base_height * slant_factor)
            extra_height = max(30, int(base_height * 0.8))
            
            width = base_width + max_offset + 10
            height = base_height + extra_height
        else:
            # 普通文本
            width = base_width
            height = base_height
        
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
        
        # 确保水印位置在图像范围内（与图片水印保持一致）
        x = max(0, min(x, img_width - text_width))
        y = max(0, min(y, img_height - text_height))
        
        # 创建一个单独的透明层来绘制文本和效果
        text_layer = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
        
        # 根据是否有旋转选择不同的绘制方式
        if self.rotation != 0:
            # 旋转情况下的绘制
            text_canvas_size = max(text_width, text_height) * 3
            text_img = Image.new('RGBA', (text_canvas_size, text_canvas_size), (0, 0, 0, 0))
            
            # 在临时画布中心位置
            text_x = (text_canvas_size - text_width) // 2
            text_y = (text_canvas_size - text_height) // 2
            
            # 绘制到临时画布
            self._draw_text_with_effects(text_img, text_x, text_y, font)
            
            # 旋转文本图像
            rotated_text = text_img.rotate(self.rotation, expand=False)
            
            # 计算粘贴位置
            paste_x = x - (text_canvas_size - text_width) // 2
            paste_y = y - (text_canvas_size - text_height) // 2
            
            # 粘贴到文本层
            text_layer.paste(rotated_text, (paste_x, paste_y), rotated_text)
        else:
            # 直接绘制（无旋转）
            self._draw_text_with_effects(text_layer, x, y, font)
        
        # 合并文本层到主图像
        watermarked_image = Image.alpha_composite(watermarked_image, text_layer)
        
        return watermarked_image
    
    def _draw_text_with_effects(self, image: Image.Image, x: int, y: int, font: ImageFont.ImageFont):
        """在图像上绘制带效果的文本
        
        Args:
            image: 目标图像
            x: 文本X坐标
            y: 文本Y坐标
            font: 字体对象
        """
        draw = ImageDraw.Draw(image)
        
        # 1. 绘制阴影（如果启用）
        if self.shadow_enabled:
            shadow_x = x + self.shadow_offset[0]
            shadow_y = y + self.shadow_offset[1]
            
            if self.shadow_blur > 0:
                # 创建模糊阴影
                shadow_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow_layer)
                shadow_draw.text((shadow_x, shadow_y), self.text, font=font, fill=self.shadow_color)
                
                # 应用模糊效果（简化版，使用多次偏移绘制模拟模糊）
                for i in range(self.shadow_blur):
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                blur_x = shadow_x + dx * (i + 1)
                                blur_y = shadow_y + dy * (i + 1)
                                # 降低透明度来模拟模糊效果
                                blur_color = (*self.shadow_color[:3], self.shadow_color[3] // (i + 2))
                                shadow_draw.text((blur_x, blur_y), self.text, font=font, fill=blur_color)
                
                # 合并阴影层
                image = Image.alpha_composite(image, shadow_layer)
                draw = ImageDraw.Draw(image)
            else:
                # 直接绘制阴影
                draw.text((shadow_x, shadow_y), self.text, font=font, fill=self.shadow_color)
        
        # 2. 绘制描边（如果启用）
        if self.stroke_enabled and self.stroke_width > 0:
            # 在主文本周围绘制描边
            for dx in range(-self.stroke_width, self.stroke_width + 1):
                for dy in range(-self.stroke_width, self.stroke_width + 1):
                    if dx != 0 or dy != 0:
                        # 计算距离，只在描边宽度内绘制
                        distance = (dx * dx + dy * dy) ** 0.5
                        if distance <= self.stroke_width:
                            stroke_x = x + dx
                            stroke_y = y + dy
                            draw.text((stroke_x, stroke_y), self.text, font=font, fill=self.stroke_color)
        
        # 3. 绘制主文本
        if self.font_bold and self.font_italic:
            # 粗斜体效果：先应用斜体变换，再用粗体方法增强
            self._draw_bold_italic_shear(draw, x, y, font)
        elif self.font_bold:
            # 模拟粗体效果：在周围绘制多次，使用安全绘制
            self._draw_safe_bold_text(draw, x, y, font)
        elif self.font_italic:
            # 真正的斜体效果：字体倾斜变形
            self._draw_italic_shear(draw, x, y, font)
        else:
            # 普通文本也使用安全的绘制方法，确保不会超出边界
            self._draw_safe_text(draw, x, y, font)
    
    def _draw_safe_text(self, draw: ImageDraw.ImageDraw, x: int, y: int, font: ImageFont.ImageFont):
        """绘制普通文本，采用与斜体完全相同的临时画布模式"""
        try:
            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = (len(self.text) * 10, 20)
        
        # 创建临时画布（根据字体自适应计算额外高度）
        padding = 5
        # 根据字体特性自适应计算额外高度
        extra_height = self._calculate_font_extra_height(font, text_height)
        temp_width = text_width + padding * 2
        temp_height = text_height + extra_height + padding
        
        # 创建临时图像
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 在临时图像上绘制文本（参考斜体的位置分布）
        text_x = padding
        text_y = extra_height // 3  # 顶部留出1/3的extra空间，底部留出2/3
        temp_draw.text((text_x, text_y), self.text, font=font, fill=self.font_color)
        
        # 计算粘贴位置（模仿斜体的位置计算）
        paste_x = x - text_x
        paste_y = y - text_y
        
        # 确保粘贴位置不会超出图像边界并执行粘贴（完全模仿斜体的做法）
        if hasattr(draw, '_image'):
            main_img = draw._image
            paste_x = max(0, min(paste_x, main_img.width - temp_width))
            paste_y = max(0, min(paste_y, main_img.height - temp_height))
            main_img.paste(temp_img, (paste_x, paste_y), temp_img)
        else:
            # 回退方案：直接绘制
            draw.text((x, y), self.text, font=font, fill=self.font_color)
    
    def _draw_safe_bold_text(self, draw: ImageDraw.ImageDraw, x: int, y: int, font: ImageFont.ImageFont):
        """绘制粗体文本，采用与斜体完全相同的临时画布模式"""
        try:
            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = (len(self.text) * 10, 20)
        
        # 创建临时画布（根据字体自适应计算额外高度，并容纳粗体扩展）
        padding = 5
        bold_extra = 2  # 粗体额外空间
        # 根据字体特性自适应计算额外高度
        extra_height = self._calculate_font_extra_height(font, text_height)
        temp_width = text_width + padding * 2 + bold_extra
        temp_height = text_height + extra_height + padding + bold_extra
        
        # 创建临时图像
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 在临时图像上绘制粗体文本（参考斜体的位置分布）
        text_x = padding
        text_y = extra_height // 3  # 顶部留出1/3的extra空间，底部留出2/3
        # 多次绘制模拟粗体效果
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                temp_draw.text((text_x + dx, text_y + dy), self.text, font=font, fill=self.font_color)
        
        # 计算粘贴位置（模仿斜体的位置计算）
        paste_x = x - text_x
        paste_y = y - text_y
        
        # 确保粘贴位置不会超出图像边界并执行粘贴（完全模仿斜体的做法）
        if hasattr(draw, '_image'):
            main_img = draw._image
            paste_x = max(0, min(paste_x, main_img.width - temp_width))
            paste_y = max(0, min(paste_y, main_img.height - temp_height))
            main_img.paste(temp_img, (paste_x, paste_y), temp_img)
        else:
            # 回退方案：直接绘制粗体
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    draw.text((x + dx, y + dy), self.text, font=font, fill=self.font_color)
    
    def _draw_italic_text(self, draw: ImageDraw.ImageDraw, x: int, y: int, font: ImageFont.ImageFont):
        """绘制斜体文本（使用图像变换实现真正的斜体效果）
        
        Args:
            draw: ImageDraw对象
            x: 文本X坐标
            y: 文本Y坐标
            font: 字体对象
        """
        # 获取文本尺寸
        try:
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # 回退方法
            text_width, text_height = draw.textsize(self.text, font=font) if hasattr(draw, 'textsize') else (100, 20)
        
        # 创建临时图像来绘制文本
        padding = max(20, text_height // 2)  # 添加足够的padding
        temp_width = text_width + padding * 2
        temp_height = text_height + padding * 2
        
        # 创建临时图像
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 在临时图像上绘制文本
        temp_draw.text((padding, padding), self.text, font=font, fill=self.font_color)
        
        # 应用斜体变换（剪切变换）
        # 使用仿射变换来创建斜体效果
        try:
            # 斜体角度约15度，对应的剪切系数为 tan(15°) ≈ 0.26
            shear_factor = 0.25  # 剪切系数
            
            # 计算变换后的尺寸
            skew_offset = int(temp_height * shear_factor)
            new_width = temp_width + skew_offset
            
            # 创建变换后的图像
            skewed_img = Image.new('RGBA', (new_width, temp_height), (0, 0, 0, 0))
            
            # 逐行进行剪切变换
            for row in range(temp_height):
                # 计算该行的偏移量（从底部到顶部逐渐增加偏移）
                progress = (temp_height - row) / temp_height
                offset = int(progress * skew_offset)
                
                # 获取原图像的这一行
                source_row = temp_img.crop((0, row, temp_width, row + 1))
                
                # 粘贴到目标位置
                if offset < new_width:
                    skewed_img.paste(source_row, (offset, row))
            
            # 计算粘贴位置
            paste_x = max(0, x - padding)
            paste_y = max(0, y - padding)
            
            # 粘贴到主图像
            if hasattr(draw, '_image'):  # 确保draw对象有_image属性
                main_img = draw._image
                main_img.paste(skewed_img, (paste_x, paste_y), skewed_img)
            else:
                # 回退方案：直接绘制普通文本
                draw.text((x, y), self.text, font=font, fill=self.font_color)
                
        except Exception:
            # 如果变换失败，回退到简单的偏移斜体
            self._draw_simple_italic(draw, x, y, font)
    
    def _draw_italic_shear(self, draw: ImageDraw.ImageDraw, x: int, y: int, font: ImageFont.ImageFont):
        """使用逐行剪切实现真正的斜体效果"""
        # 获取文本尺寸
        try:
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = (len(self.text) * 10, 20)
        
        # 斜体倾斜参数 - 减小倾斜系数，避免过度扩展
        slant_factor = 0.15  # 更合理的倾斜系数（约8-10度）
        max_offset = int(text_height * slant_factor)  # 最大偏移量
        
        # 重新计算临时画布尺寸，确保高度充足
        # 水平方向：只需要为斜体偏移留出空间（去除固定buffer）
        temp_width = text_width + max_offset
        
        # 垂直方向：确保有足够空间容纳完整文本
        # 为descenders（g, j, p, q, y等）和不同字体的高度变化预留更多空间
        extra_height = int(text_height * 0.6)  # 文本高度的60%作为额外空间
        temp_height = text_height + extra_height
        
        # 简化padding，但确保文本不会被裁切（去除固定padding）
        text_x = 0   # 左边距
        text_y = extra_height // 3  # 顶部留出1/3的extra空间，底部留出2/3
        
        # 创建临时图像
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 在临时图像上绘制文本
        temp_draw.text((text_x, text_y), self.text, font=font, fill=self.font_color)
        
        # 创建倾斜后的图像
        skewed_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        
        try:
            # 逐行进行剪切变换
            for y_offset in range(temp_height):
                # 计算当前行的水平偏移量
                # 斜体效果：文字顶部向右倾斜
                # y_offset 越小（越靠近顶部），偏移量越大
                progress = 1.0 - (y_offset / temp_height) if temp_height > 0 else 0
                horizontal_offset = int(max_offset * progress)
                
                # 获取原图像的当前行
                if y_offset < temp_height:
                    source_line = temp_img.crop((0, y_offset, temp_width, y_offset + 1))
                    
                    # 将这一行粘贴到新位置（添加水平偏移）
                    if horizontal_offset >= 0 and horizontal_offset < temp_width:
                        skewed_img.paste(source_line, (horizontal_offset, y_offset))
            
            # 简化位置计算思路
            # 我们希望斜体文本的"视觉左上角"对应到目标位置(x, y)
            # 
            # 关键理解：斜体变换后，我们需要找到实际内容的左上角在哪里
            # 由于底部行没有偏移，顶部行有max_offset偏移
            # 文本的左上角实际上就是原始文本位置：(text_x, text_y)
            
            # 简单直接的位置映射
            paste_x = x
            paste_y = y - text_y
            
            
            # 确保粘贴位置不会超出图像边界并执行粘贴
            if hasattr(draw, '_image'):
                main_img = draw._image
                paste_x = max(0, min(paste_x, main_img.width - temp_width))
                paste_y = max(0, min(paste_y, main_img.height - temp_height))
                main_img.paste(skewed_img, (paste_x, paste_y), skewed_img)
            else:
                # 回退方案
                draw.text((x, y), self.text, font=font, fill=self.font_color)
                
        except Exception:
            # 如果倾斜失败，使用最简单的偏移
            offset = max(3, text_height // 8)
            draw.text((x + offset, y), self.text, font=font, fill=self.font_color)
    
    def _draw_bold_italic_shear(self, draw: ImageDraw.ImageDraw, x: int, y: int, font: ImageFont.ImageFont):
        """绘制粗斜体效果（逐行剪切 + 粗体增强）"""
        # 获取文本尺寸
        try:
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = (len(self.text) * 10, 20)
        
        # 斜体倾斜参数 - 减小倾斜系数，避免过度扩展
        slant_factor = 0.15  # 更合理的倾斜系数（约8-10度）
        max_offset = int(text_height * slant_factor)
        
        # 精确计算粗斜体画布尺寸
        # 粗体需要少量额外空间（1-2像素的偏移）
        bold_extra = 3  # 粗体额外空间
        temp_width = text_width + max_offset + bold_extra  # 总宽度控制
        
        # 垂直方向：确保有足够空间容纳完整文本
        # 为descenders（g, j, p, q, y等）和粗体效果预留更多空间
        extra_height = int(text_height * 0.6)  # 文本高度的60%作为额外空间
        temp_height = text_height + extra_height + bold_extra  # 总高度控制
        
        # 创建临时图像
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 先绘制粗体文本（多次偏移绘制）
        base_x = 0   # 左边距
        base_y = extra_height // 3  # 顶部留出1/3的extra空间，底部留出2/3
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                temp_draw.text((base_x + dx, base_y + dy), self.text, font=font, fill=self.font_color)
        
        # 创建倾斜后的图像
        skewed_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        
        try:
            # 逐行进行剪切变换
            for y_offset in range(temp_height):
                # 斜体效果：文字顶部向右倾斜
                progress = 1.0 - (y_offset / temp_height) if temp_height > 0 else 0
                horizontal_offset = int(max_offset * progress)
                
                if y_offset < temp_height:
                    source_line = temp_img.crop((0, y_offset, temp_width, y_offset + 1))
                    if horizontal_offset >= 0 and horizontal_offset < temp_width:
                        skewed_img.paste(source_line, (horizontal_offset, y_offset))
            
            # 计算正确的粘贴位置（粗斜体）
            # 使用与普通斜体相同的简化逻辑
            paste_x = x
            paste_y = y - base_y
            
            # 确保粘贴位置不会超出图像边界并执行粘贴
            if hasattr(draw, '_image'):
                main_img = draw._image
                paste_x = max(0, min(paste_x, main_img.width - temp_width))
                paste_y = max(0, min(paste_y, main_img.height - temp_height))
                main_img.paste(skewed_img, (paste_x, paste_y), skewed_img)
            else:
                # 回退：粗体 + 简单偏移
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        offset = max(3, text_height // 8)
                        draw.text((x + dx + offset, y + dy), self.text, font=font, fill=self.font_color)
                        
        except Exception:
            # 回退：粗体 + 简单偏移
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    offset = max(3, text_height // 8)
                    draw.text((x + dx + offset, y + dy), self.text, font=font, fill=self.font_color)
    
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
    """图片水印类"""
    
    def __init__(self):
        """初始化图片水印"""
        self.watermark_image = None
        self.original_watermark = None  # 保存原始图片，用于缩放
        self.position = (0.5, 0.5)
        self.scale = 1.0  # 缩放比例 (0.1-5.0)
        self.transparency = 100  # 不透明度 (0-100)
        self.rotation = 0  # 旋转角度
        self.image_path = ""  # 图片路径，用于配置保存
        
    def load_watermark_image(self, image_path: str) -> bool:
        """加载水印图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            bool: 是否加载成功
        """
        try:
            self.original_watermark = Image.open(image_path)
            # 确保为RGBA模式以支持透明通道
            if self.original_watermark.mode != 'RGBA':
                self.original_watermark = self.original_watermark.convert('RGBA')
            
            # 初始化当前水印图像
            self.watermark_image = self.original_watermark.copy()
            # 保存图片路径
            self.image_path = image_path
            return True
        except FileNotFoundError:
            print(f"错误: 水印图片文件不存在 - {image_path}")
            return False
        except PermissionError:
            print(f"错误: 没有权限访问水印图片 - {image_path}")
            return False
        except Exception as e:
            error_msg = str(e)
            if "cannot identify image file" in error_msg.lower():
                print(f"错误: 不支持的图片格式 - {image_path}")
            elif "truncated" in error_msg.lower():
                print(f"错误: 图片文件损坏 - {image_path}")
            else:
                print(f"错误: 加载水印图片失败 - {image_path}: {error_msg}")
            return False
    
    def set_scale(self, scale: float):
        """设置缩放比例
        
        Args:
            scale: 缩放比例 (0.1-5.0)
        """
        self.scale = max(0.1, min(5.0, scale))
        self._update_watermark_image()
    
    def set_transparency(self, transparency: int):
        """设置透明度
        
        Args:
            transparency: 不透明度 (0-100)
        """
        self.transparency = max(0, min(100, transparency))
        self._update_watermark_image()
    
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
        self._update_watermark_image()
    
    def _update_watermark_image(self):
        """更新水印图像（应用缩放、透明度、旋转）"""
        if self.original_watermark is None:
            return
        
        # 从原始图像开始
        watermark = self.original_watermark.copy()
        
        # 应用缩放
        if self.scale != 1.0:
            new_width = int(watermark.width * self.scale)
            new_height = int(watermark.height * self.scale)
            watermark = watermark.resize((new_width, new_height), Image.Resampling.BICUBIC)
        
        # 应用透明度
        if self.transparency < 100:
            # 调整整个图像的alpha通道
            alpha = watermark.split()[-1]  # 获取alpha通道
            alpha = alpha.point(lambda p: int(p * self.transparency / 100))
            watermark.putalpha(alpha)
        
        # 应用旋转
        if abs(self.rotation) > 0.1:
            try:
                watermark = watermark.rotate(
                    self.rotation,
                    expand=True,  # 扩展画布以容纳旋转后的图像
                    fillcolor=(0, 0, 0, 0),
                    resample=Image.Resampling.BICUBIC
                )
            except Exception as e:
                print(f"Warning: 旋转失败，使用NEAREST插值: {e}")
                try:
                    watermark = watermark.rotate(
                        self.rotation,
                        expand=True,
                        fillcolor=(0, 0, 0, 0),
                        resample=Image.Resampling.NEAREST
                    )
                except Exception as e2:
                    print(f"Warning: 旋转完全失败，跳过旋转: {e2}")
                    # 如果旋转失败，继续使用原图像
        
        self.watermark_image = watermark
    
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
    
    def apply_to_image(self, image: Image.Image) -> Image.Image:
        """将图片水印应用到图像
        
        Args:
            image: 原始图像
            
        Returns:
            Image.Image: 添加水印后的图像
        """
        if self.watermark_image is None or self.transparency == 0:
            return image.copy()
        
        # 创建图像副本
        watermarked_image = image.copy()
        
        # 确保图像为RGBA模式以支持透明度
        if watermarked_image.mode != 'RGBA':
            watermarked_image = watermarked_image.convert('RGBA')
        
        # 获取水印尺寸
        watermark_width, watermark_height = self.watermark_image.size
        img_width, img_height = watermarked_image.size
        
        # 计算水印位置
        x = int((img_width - watermark_width) * self.position[0])
        y = int((img_height - watermark_height) * self.position[1])
        
        # 确保水印位置在图像范围内
        x = max(0, min(x, img_width - watermark_width))
        y = max(0, min(y, img_height - watermark_height))
        
        # 创建一个透明层来绘制水印
        watermark_layer = Image.new('RGBA', watermarked_image.size, (0, 0, 0, 0))
        
        # 粘贴水印到透明层
        watermark_layer.paste(self.watermark_image, (x, y), self.watermark_image)
        
        # 合并水印层到主图像
        watermarked_image = Image.alpha_composite(watermarked_image, watermark_layer)
        
        return watermarked_image
