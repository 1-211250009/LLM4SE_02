#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Error Handler
错误处理工具类
"""

from PySide6.QtWidgets import QMessageBox
from typing import Optional


class ErrorHandler:
    """错误处理工具类"""
    
    @staticmethod
    def show_error_dialog(parent, title: str, message: str, details: Optional[str] = None):
        """显示错误对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 错误消息
            details: 详细信息（可选）
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    @staticmethod
    def show_warning_dialog(parent, title: str, message: str, details: Optional[str] = None):
        """显示警告对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 警告消息
            details: 详细信息（可选）
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    @staticmethod
    def show_info_dialog(parent, title: str, message: str):
        """显示信息对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 信息消息
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    @staticmethod
    def format_file_error(error_type: str, file_path: str, details: str = "") -> str:
        """格式化文件错误消息
        
        Args:
            error_type: 错误类型
            file_path: 文件路径
            details: 详细信息
            
        Returns:
            str: 格式化的错误消息
        """
        filename = file_path.split('/')[-1] if '/' in file_path else file_path
        
        error_messages = {
            'not_found': f"文件不存在: {filename}",
            'permission': f"没有权限访问文件: {filename}",
            'format': f"不支持的图片格式: {filename}",
            'corrupted': f"图片文件损坏: {filename}",
            'too_large': f"文件过大: {filename}",
            'network': f"网络错误，无法访问文件: {filename}"
        }
        
        message = error_messages.get(error_type, f"处理文件时出错: {filename}")
        
        if details:
            message += f"\n详细信息: {details}"
        
        return message
