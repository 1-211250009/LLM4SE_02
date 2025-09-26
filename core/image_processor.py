#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Image Processor
图片处理核心模块
"""

import os
from typing import List, Optional, Tuple
from PIL import Image, ImageFile
import mimetypes


class ImageProcessor:
    """图片处理器类"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
    }
    
    # 输出格式
    OUTPUT_FORMATS = ['JPEG', 'PNG']
    
    def __init__(self):
        """初始化图片处理器"""
        # 支持加载不完整的图片
        ImageFile.LOAD_TRUNCATED_IMAGES = True
    
    def is_supported_format(self, file_path: str) -> bool:
        """检查文件格式是否支持
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持的格式
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.SUPPORTED_FORMATS
    
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """加载图片文件
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            PIL.Image.Image or None: 加载的图片对象，失败返回None
        """
        try:
            if not self.is_supported_format(file_path):
                return None
                
            image = Image.open(file_path)
            # 转换为RGB模式（如果需要）
            if image.mode in ('RGBA', 'LA', 'P'):
                # 保持透明通道
                if image.mode == 'P' and 'transparency' in image.info:
                    image = image.convert('RGBA')
                elif image.mode != 'RGBA':
                    image = image.convert('RGBA')
            elif image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
                
            return image
        except Exception as e:
            print(f"加载图片失败 {file_path}: {e}")
            return None
    
    def get_image_info(self, file_path: str) -> Optional[dict]:
        """获取图片信息
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            dict or None: 图片信息字典
        """
        try:
            image = self.load_image(file_path)
            if image is None:
                return None
                
            file_size = os.path.getsize(file_path)
            
            return {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'size': image.size,  # (width, height)
                'mode': image.mode,
                'format': image.format,
                'file_size': file_size,
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
        except Exception as e:
            print(f"获取图片信息失败 {file_path}: {e}")
            return None
    
    def create_thumbnail(self, image: Image.Image, size: Tuple[int, int] = (150, 150)) -> Image.Image:
        """创建缩略图
        
        Args:
            image: PIL图片对象
            size: 缩略图尺寸
            
        Returns:
            PIL.Image.Image: 缩略图
        """
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail
    
    def save_image(self, image: Image.Image, output_path: str, 
                   format_type: str = 'JPEG', quality: int = 95) -> bool:
        """保存图片
        
        Args:
            image: PIL图片对象
            output_path: 输出路径
            format_type: 输出格式 ('JPEG' 或 'PNG')
            quality: JPEG质量 (0-100)
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 根据格式处理图片
            if format_type.upper() == 'JPEG':
                # JPEG不支持透明通道，需要转换
                if image.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])
                    else:
                        background.paste(image)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            elif format_type.upper() == 'PNG':
                # PNG支持透明通道
                if image.mode not in ('RGBA', 'RGB', 'P'):
                    image = image.convert('RGBA')
                
                image.save(output_path, 'PNG', optimize=True)
            
            return True
            
        except Exception as e:
            print(f"保存图片失败 {output_path}: {e}")
            return False
    
    def generate_output_filename(self, original_path: str, output_dir: str,
                                naming_rule: str = 'original', 
                                prefix: str = '', suffix: str = '',
                                output_format: str = 'JPEG') -> str:
        """生成输出文件名
        
        Args:
            original_path: 原始文件路径
            output_dir: 输出目录
            naming_rule: 命名规则 ('original', 'prefix', 'suffix')
            prefix: 前缀
            suffix: 后缀
            output_format: 输出格式
            
        Returns:
            str: 输出文件路径
        """
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        
        # 根据命名规则生成文件名
        if naming_rule == 'prefix' and prefix:
            filename = f"{prefix}{base_name}"
        elif naming_rule == 'suffix' and suffix:
            filename = f"{base_name}{suffix}"
        else:  # 'original'
            filename = base_name
        
        # 添加格式扩展名
        if output_format.upper() == 'JPEG':
            ext = '.jpg'
        else:
            ext = '.png'
        
        return os.path.join(output_dir, f"{filename}{ext}")
