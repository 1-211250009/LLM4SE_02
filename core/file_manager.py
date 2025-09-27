#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - File Manager
文件管理模块
"""

import os
from typing import List, Optional
from .image_processor import ImageProcessor


class FileManager:
    """文件管理器类"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.image_processor = ImageProcessor()
        self.loaded_images = []  # 存储已加载的图片信息
        self.selected_indices = set()  # 存储选中的图片索引
    
    def add_single_image(self, file_path: str) -> bool:
        """添加单张图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 是否成功添加
        """
        if not os.path.exists(file_path):
            return False
        
        if not self.image_processor.is_supported_format(file_path):
            return False
        
        # 检查是否已经添加过
        if any(img['path'] == file_path for img in self.loaded_images):
            return False
        
        # 获取图片信息
        image_info = self.image_processor.get_image_info(file_path)
        if image_info:
            self.loaded_images.append(image_info)
            return True
        
        return False
    
    def add_multiple_images(self, file_paths: List[str]) -> int:
        """添加多张图片
        
        Args:
            file_paths: 图片文件路径列表
            
        Returns:
            int: 成功添加的图片数量
        """
        success_count = 0
        for file_path in file_paths:
            if self.add_single_image(file_path):
                success_count += 1
        return success_count
    
    def add_folder(self, folder_path: str, recursive: bool = False) -> int:
        """添加文件夹中的所有图片
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归子文件夹
            
        Returns:
            int: 成功添加的图片数量
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return 0
        
        image_files = []
        
        if recursive:
            # 递归遍历所有子文件夹
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.image_processor.is_supported_format(file_path):
                        image_files.append(file_path)
        else:
            # 只遍历当前文件夹
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and self.image_processor.is_supported_format(file_path):
                    image_files.append(file_path)
        
        return self.add_multiple_images(image_files)
    
    def remove_image(self, index: int) -> bool:
        """移除指定索引的图片
        
        Args:
            index: 图片索引
            
        Returns:
            bool: 是否成功移除
        """
        if 0 <= index < len(self.loaded_images):
            self.loaded_images.pop(index)
            return True
        return False
    
    def remove_image_by_path(self, file_path: str) -> bool:
        """根据路径移除图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 是否成功移除
        """
        for i, img in enumerate(self.loaded_images):
            if img['path'] == file_path:
                self.loaded_images.pop(i)
                return True
        return False
    
    def clear_all_images(self):
        """清空所有已加载的图片"""
        self.loaded_images.clear()
        self.selected_indices.clear()
    
    def get_image_list(self) -> List[dict]:
        """获取已加载的图片列表
        
        Returns:
            List[dict]: 图片信息列表
        """
        return self.loaded_images.copy()
    
    def get_image_count(self) -> int:
        """获取已加载的图片数量
        
        Returns:
            int: 图片数量
        """
        return len(self.loaded_images)
    
    def get_image_info(self, index: int) -> Optional[dict]:
        """获取指定索引的图片信息
        
        Args:
            index: 图片索引
            
        Returns:
            dict or None: 图片信息
        """
        if 0 <= index < len(self.loaded_images):
            return self.loaded_images[index]
        return None
    
    def validate_output_directory(self, output_dir: str, prevent_overwrite: bool = True) -> tuple:
        """验证输出目录
        
        Args:
            output_dir: 输出目录路径
            prevent_overwrite: 是否禁止覆盖原文件夹
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not output_dir:
            return False, "请选择输出目录"
        
        # 检查目录是否存在，不存在则尝试创建
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except PermissionError:
                return False, "没有权限创建输出目录"
            except OSError as e:
                if "No space left on device" in str(e):
                    return False, "磁盘空间不足，无法创建目录"
                else:
                    return False, f"创建目录失败: {e}"
            except Exception as e:
                return False, f"创建输出目录时发生未知错误: {e}"
        
        if not os.path.isdir(output_dir):
            return False, "输出路径不是有效的目录"
        
        # 检查是否有写入权限
        if not os.access(output_dir, os.W_OK):
            return False, "没有输出目录的写入权限"
        
        # 检查是否与原文件目录重复
        if prevent_overwrite:
            for img_info in self.loaded_images:
                img_dir = os.path.dirname(img_info['path'])
                if os.path.samefile(output_dir, img_dir):
                    return False, "为防止覆盖原图，不能输出到原文件所在目录"
        
        return True, ""
    
    def get_supported_formats_filter(self) -> str:
        """获取文件对话框的格式过滤器
        
        Returns:
            str: 格式过滤器字符串
        """
        formats = []
        formats.append("支持的图片格式 (*.jpg *.jpeg *.png *.bmp *.tiff *.tif)")
        formats.append("JPEG 图片 (*.jpg *.jpeg)")
        formats.append("PNG 图片 (*.png)")
        formats.append("BMP 图片 (*.bmp)")
        formats.append("TIFF 图片 (*.tiff *.tif)")
        formats.append("所有文件 (*.*)")
        
        return ";;".join(formats)
    
    def set_selected(self, index: int, selected: bool = True):
        """设置图片选中状态
        
        Args:
            index: 图片索引
            selected: 是否选中
        """
        if 0 <= index < len(self.loaded_images):
            if selected:
                self.selected_indices.add(index)
            else:
                self.selected_indices.discard(index)
    
    def toggle_selected(self, index: int):
        """切换图片选中状态
        
        Args:
            index: 图片索引
        """
        if 0 <= index < len(self.loaded_images):
            if index in self.selected_indices:
                self.selected_indices.remove(index)
            else:
                self.selected_indices.add(index)
    
    def is_selected(self, index: int) -> bool:
        """检查图片是否选中
        
        Args:
            index: 图片索引
            
        Returns:
            bool: 是否选中
        """
        return index in self.selected_indices
    
    def get_selected_indices(self) -> List[int]:
        """获取所有选中的图片索引
        
        Returns:
            List[int]: 选中的索引列表
        """
        return sorted(list(self.selected_indices))
    
    def get_selected_images(self) -> List[dict]:
        """获取所有选中的图片信息
        
        Returns:
            List[dict]: 选中的图片信息列表
        """
        selected_images = []
        for index in sorted(self.selected_indices):
            if 0 <= index < len(self.loaded_images):
                selected_images.append(self.loaded_images[index])
        return selected_images
    
    def select_all(self):
        """全选所有图片"""
        self.selected_indices = set(range(len(self.loaded_images)))
    
    def clear_selection(self):
        """清空选择"""
        self.selected_indices.clear()
    
    def get_selected_count(self) -> int:
        """获取选中图片数量
        
        Returns:
            int: 选中的图片数量
        """
        return len(self.selected_indices)
