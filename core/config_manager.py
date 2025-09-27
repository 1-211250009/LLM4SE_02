#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Configuration Manager
配置管理器
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .watermark import TextWatermark, ImageWatermark


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self):
        """初始化配置管理器"""
        # 配置文件存储目录
        self.config_dir = Path.home() / ".photo_watermark_templates"
        self.config_dir.mkdir(exist_ok=True)
        
        # 最后使用的设置文件
        self.last_settings_file = self.config_dir / "last_settings.json"
        
        # 模板文件目录
        self.templates_dir = self.config_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
    
    def save_template(self, name: str, description: str, text_watermark: TextWatermark, 
                     image_watermark: ImageWatermark, active_watermark: str) -> bool:
        """保存水印模板
        
        Args:
            name: 模板名称
            description: 模板描述
            text_watermark: 文本水印对象
            image_watermark: 图片水印对象
            active_watermark: 当前激活的水印类型 ("text" 或 "image")
            
        Returns:
            bool: 是否保存成功
        """
        try:
            template_data = {
                "template_name": name,
                "template_description": description,
                "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text_watermark": self._serialize_text_watermark(text_watermark),
                "image_watermark": self._serialize_image_watermark(image_watermark),
                "active_watermark": active_watermark
            }
            
            # 生成安全的文件名
            safe_name = self._get_safe_filename(name)
            template_file = self.templates_dir / f"{safe_name}.json"
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
        except PermissionError:
            print(f"错误: 没有权限保存模板到 {self.templates_dir}")
            return False
        except OSError as e:
            if "No space left on device" in str(e):
                print(f"错误: 磁盘空间不足，无法保存模板")
            else:
                print(f"错误: 文件系统错误，保存模板失败: {e}")
            return False
        except Exception as e:
            print(f"错误: 保存模板失败: {e}")
            return False
    
    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """加载水印模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            Dict[str, Any]: 模板数据，如果失败返回None
        """
        try:
            safe_name = self._get_safe_filename(template_name)
            template_file = self.templates_dir / f"{safe_name}.json"
            
            if not template_file.exists():
                return None
            
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误: 模板文件不存在 - {template_name}")
            return None
        except PermissionError:
            print(f"错误: 没有权限读取模板文件 - {template_name}")
            return None
        except json.JSONDecodeError:
            print(f"错误: 模板文件格式错误 - {template_name}")
            return None
        except Exception as e:
            print(f"错误: 加载模板失败 - {template_name}: {e}")
            return None
    
    def get_template_list(self) -> List[Dict[str, str]]:
        """获取所有模板列表
        
        Returns:
            List[Dict[str, str]]: 模板信息列表
        """
        templates = []
        try:
            for template_file in self.templates_dir.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    templates.append({
                        "name": data.get("template_name", "未命名模板"),
                        "description": data.get("template_description", ""),
                        "created_time": data.get("created_time", ""),
                        "filename": template_file.stem
                    })
                except Exception as e:
                    print(f"读取模板文件 {template_file} 失败: {e}")
                    continue
        except Exception as e:
            print(f"获取模板列表失败: {e}")
        
        # 按创建时间排序
        templates.sort(key=lambda x: x.get("created_time", ""), reverse=True)
        return templates
    
    def delete_template(self, template_name: str) -> bool:
        """删除水印模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            bool: 是否删除成功
        """
        try:
            safe_name = self._get_safe_filename(template_name)
            template_file = self.templates_dir / f"{safe_name}.json"
            
            if template_file.exists():
                template_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False
    
    def save_last_settings(self, text_watermark: TextWatermark, 
                          image_watermark: ImageWatermark, active_watermark: str) -> bool:
        """保存最后使用的设置
        
        Args:
            text_watermark: 文本水印对象
            image_watermark: 图片水印对象
            active_watermark: 当前激活的水印类型
            
        Returns:
            bool: 是否保存成功
        """
        try:
            settings_data = {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text_watermark": self._serialize_text_watermark(text_watermark),
                "image_watermark": self._serialize_image_watermark(image_watermark),
                "active_watermark": active_watermark
            }
            
            with open(self.last_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存最后设置失败: {e}")
            return False
    
    def load_last_settings(self) -> Optional[Dict[str, Any]]:
        """加载最后使用的设置
        
        Returns:
            Dict[str, Any]: 设置数据，如果失败返回None
        """
        try:
            if not self.last_settings_file.exists():
                return None
            
            with open(self.last_settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载最后设置失败: {e}")
            return None
    
    def apply_template_to_watermarks(self, template_data: Dict[str, Any], 
                                   text_watermark: TextWatermark, 
                                   image_watermark: ImageWatermark) -> str:
        """将模板数据应用到水印对象
        
        Args:
            template_data: 模板数据
            text_watermark: 文本水印对象
            image_watermark: 图片水印对象
            
        Returns:
            str: 激活的水印类型
        """
        try:
            # 应用文本水印设置
            if "text_watermark" in template_data:
                self._deserialize_text_watermark(template_data["text_watermark"], text_watermark)
            
            # 应用图片水印设置
            if "image_watermark" in template_data:
                self._deserialize_image_watermark(template_data["image_watermark"], image_watermark)
            
            return template_data.get("active_watermark", "text")
        except Exception as e:
            print(f"应用模板失败: {e}")
            return "text"
    
    def _serialize_text_watermark(self, watermark: TextWatermark) -> Dict[str, Any]:
        """序列化文本水印对象"""
        return {
            "text": watermark.text,
            "font_size": watermark.font_size,
            "font_color": list(watermark.font_color),
            "position": list(watermark.position),
            "rotation": watermark.rotation,
            "font_family": watermark.font_family,
            "font_bold": watermark.font_bold,
            "font_italic": watermark.font_italic,
            "shadow_enabled": watermark.shadow_enabled,
            "shadow_offset": list(watermark.shadow_offset),
            "shadow_color": list(watermark.shadow_color),
            "shadow_blur": watermark.shadow_blur,
            "stroke_enabled": watermark.stroke_enabled,
            "stroke_width": watermark.stroke_width,
            "stroke_color": list(watermark.stroke_color)
        }
    
    def _serialize_image_watermark(self, watermark: ImageWatermark) -> Dict[str, Any]:
        """序列化图片水印对象"""
        # 获取图片路径（如果有的话）
        image_path = ""
        if hasattr(watermark, 'image_path'):
            image_path = watermark.image_path
        
        return {
            "image_path": image_path,
            "position": list(watermark.position),
            "scale": watermark.scale,
            "transparency": watermark.transparency,
            "rotation": watermark.rotation
        }
    
    def _deserialize_text_watermark(self, data: Dict[str, Any], watermark: TextWatermark):
        """反序列化文本水印对象"""
        watermark.set_text(data.get("text", "Photo Watermark"))
        watermark.set_font_size(data.get("font_size", 60))
        
        # 设置颜色和透明度
        font_color = data.get("font_color", [255, 255, 255, 255])
        if len(font_color) >= 4:
            watermark.font_color = tuple(font_color)
        
        # 设置位置
        position = data.get("position", [0.95, 0.95])
        if len(position) >= 2:
            watermark.set_position(position[0], position[1])
        
        watermark.set_rotation(data.get("rotation", 0))
        watermark.set_font_family(data.get("font_family", "默认字体"))
        watermark.set_font_style(
            bold=data.get("font_bold", False),
            italic=data.get("font_italic", False)
        )
        
        # 设置阴影
        shadow_offset = data.get("shadow_offset", [2, 2])
        shadow_color = data.get("shadow_color", [0, 0, 0, 128])
        watermark.set_shadow(
            enabled=data.get("shadow_enabled", False),
            offset=tuple(shadow_offset) if len(shadow_offset) >= 2 else (2, 2),
            color=tuple(shadow_color) if len(shadow_color) >= 4 else (0, 0, 0, 128),
            blur=data.get("shadow_blur", 0)
        )
        
        # 设置描边
        stroke_color = data.get("stroke_color", [0, 0, 0, 255])
        watermark.set_stroke(
            enabled=data.get("stroke_enabled", False),
            width=data.get("stroke_width", 2),
            color=tuple(stroke_color) if len(stroke_color) >= 4 else (0, 0, 0, 255)
        )
    
    def _deserialize_image_watermark(self, data: Dict[str, Any], watermark: ImageWatermark):
        """反序列化图片水印对象"""
        # 设置位置
        position = data.get("position", [0.5, 0.5])
        if len(position) >= 2:
            watermark.set_position(position[0], position[1])
        
        watermark.set_scale(data.get("scale", 1.0))
        watermark.set_transparency(data.get("transparency", 70))
        watermark.set_rotation(data.get("rotation", 0))
        
        # 加载图片（如果路径存在且有效）
        image_path = data.get("image_path", "")
        if image_path and os.path.exists(image_path):
            watermark.load_watermark_image(image_path)
            # 保存图片路径以便后续序列化
            watermark.image_path = image_path
    
    def _get_safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        # 移除或替换不安全的字符
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        safe_name = ""
        for char in name:
            if char in safe_chars:
                safe_name += char
            elif char == " ":
                safe_name += "_"
            else:
                safe_name += "_"
        
        # 限制长度
        return safe_name[:50] if safe_name else "template"
