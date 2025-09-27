#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Template Management Dialog
模板管理对话框
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QListWidget, QListWidgetItem,
                               QTextEdit, QMessageBox, QGroupBox, QSplitter,
                               QWidget, QGridLayout, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.config_manager import ConfigManager


class TemplateDialog(QDialog):
    """模板管理对话框"""
    
    # 信号定义
    template_loaded = Signal(str)  # 模板加载信号，传递模板名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.init_ui()
        self.refresh_template_list()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("水印模板管理")
        self.setGeometry(200, 200, 800, 600)
        self.setMinimumSize(600, 400)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：模板列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)
        
        # 模板列表标题
        list_label = QLabel("已保存的模板")
        list_label.setFont(QFont("", 12, QFont.Bold))
        left_layout.addWidget(list_label)
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.setMinimumWidth(250)
        self.template_list.itemSelectionChanged.connect(self.on_template_selected)
        left_layout.addWidget(self.template_list)
        
        # 列表操作按钮
        list_buttons_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_template_list)
        list_buttons_layout.addWidget(self.refresh_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_selected_template)
        self.delete_btn.setEnabled(False)
        list_buttons_layout.addWidget(self.delete_btn)
        
        list_buttons_layout.addStretch()
        left_layout.addLayout(list_buttons_layout)
        
        splitter.addWidget(left_widget)
        
        # 右侧：模板详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)
        
        # 模板详情标题
        detail_label = QLabel("模板详情")
        detail_label.setFont(QFont("", 12, QFont.Bold))
        right_layout.addWidget(detail_label)
        
        # 模板信息显示区域
        info_group = QGroupBox("基本信息")
        info_layout = QGridLayout(info_group)
        
        # 模板名称
        info_layout.addWidget(QLabel("名称:"), 0, 0)
        self.name_label = QLabel("未选择模板")
        self.name_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(self.name_label, 0, 1)
        
        # 创建时间
        info_layout.addWidget(QLabel("创建时间:"), 1, 0)
        self.time_label = QLabel("-")
        info_layout.addWidget(self.time_label, 1, 1)
        
        # 模板描述
        info_layout.addWidget(QLabel("描述:"), 2, 0, Qt.AlignTop)
        self.description_label = QLabel("-")
        self.description_label.setWordWrap(True)
        self.description_label.setMinimumHeight(60)
        self.description_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border: 1px solid #dee2e6; border-radius: 4px;")
        info_layout.addWidget(self.description_label, 2, 1)
        
        right_layout.addWidget(info_group)
        
        # 模板配置预览
        preview_group = QGroupBox("配置预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.config_preview = QTextEdit()
        self.config_preview.setReadOnly(True)
        self.config_preview.setMaximumHeight(200)
        self.config_preview.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px;")
        preview_layout.addWidget(self.config_preview)
        
        right_layout.addWidget(preview_group)
        
        # 操作按钮
        action_buttons_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("加载模板")
        self.load_btn.clicked.connect(self.load_selected_template)
        self.load_btn.setEnabled(False)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        action_buttons_layout.addWidget(self.load_btn)
        
        action_buttons_layout.addStretch()
        right_layout.addLayout(action_buttons_layout)
        
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([300, 500])
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)
        
        main_layout.addLayout(bottom_layout)
    
    def refresh_template_list(self):
        """刷新模板列表"""
        self.template_list.clear()
        templates = self.config_manager.get_template_list()
        
        for template in templates:
            item = QListWidgetItem()
            item.setText(template["name"])
            item.setData(Qt.UserRole, template)
            
            # 设置工具提示
            tooltip = f"名称: {template['name']}\n"
            if template['description']:
                tooltip += f"描述: {template['description']}\n"
            tooltip += f"创建时间: {template['created_time']}"
            item.setToolTip(tooltip)
            
            self.template_list.addItem(item)
        
        # 清空详情显示
        self.clear_template_details()
    
    def on_template_selected(self):
        """模板选择事件"""
        current_item = self.template_list.currentItem()
        if current_item:
            template_data = current_item.data(Qt.UserRole)
            self.show_template_details(template_data)
            self.load_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
        else:
            self.clear_template_details()
            self.load_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
    def show_template_details(self, template_data):
        """显示模板详情"""
        self.name_label.setText(template_data["name"])
        self.time_label.setText(template_data["created_time"])
        self.description_label.setText(template_data["description"] if template_data["description"] else "无描述")
        
        # 加载完整的模板配置用于预览
        full_template = self.config_manager.load_template(template_data["name"])
        if full_template:
            self.show_config_preview(full_template)
    
    def show_config_preview(self, template_data):
        """显示配置预览"""
        preview_text = ""
        
        # 显示激活的水印类型
        active_type = template_data.get("active_watermark", "text")
        preview_text += f"激活水印: {'文本水印' if active_type == 'text' else '图片水印'}\n\n"
        
        # 文本水印配置
        if "text_watermark" in template_data:
            text_config = template_data["text_watermark"]
            preview_text += "【文本水印配置】\n"
            preview_text += f"  文本: {text_config.get('text', 'N/A')}\n"
            preview_text += f"  字体大小: {text_config.get('font_size', 'N/A')}px\n"
            preview_text += f"  字体: {text_config.get('font_family', 'N/A')}\n"
            
            # 字体样式
            styles = []
            if text_config.get('font_bold', False):
                styles.append("粗体")
            if text_config.get('font_italic', False):
                styles.append("斜体")
            preview_text += f"  样式: {', '.join(styles) if styles else '普通'}\n"
            
            # 颜色和透明度
            color = text_config.get('font_color', [255, 255, 255, 255])
            transparency = int(color[3] / 255 * 100) if len(color) > 3 else 100
            preview_text += f"  颜色: RGB({color[0]}, {color[1]}, {color[2]})\n"
            preview_text += f"  透明度: {transparency}%\n"
            
            # 位置
            pos = text_config.get('position', [0.0, 0.0])
            preview_text += f"  位置: ({pos[0]:.2f}, {pos[1]:.2f})\n"
            
            # 旋转
            rotation = text_config.get('rotation', 0)
            preview_text += f"  旋转: {rotation}°\n"
            
            # 特效
            effects = []
            if text_config.get('shadow_enabled', False):
                effects.append("阴影")
            if text_config.get('stroke_enabled', False):
                effects.append("描边")
            preview_text += f"  特效: {', '.join(effects) if effects else '无'}\n"
        
        # 图片水印配置
        if "image_watermark" in template_data:
            image_config = template_data["image_watermark"]
            preview_text += "\n【图片水印配置】\n"
            
            image_path = image_config.get('image_path', '')
            if image_path:
                import os
                preview_text += f"  图片: {os.path.basename(image_path)}\n"
            else:
                preview_text += "  图片: 未设置\n"
            
            preview_text += f"  缩放: {image_config.get('scale', 1.0):.2f}x\n"
            preview_text += f"  透明度: {image_config.get('transparency', 70)}%\n"
            
            # 位置
            pos = image_config.get('position', [0.5, 0.5])
            preview_text += f"  位置: ({pos[0]:.2f}, {pos[1]:.2f})\n"
            
            # 旋转
            rotation = image_config.get('rotation', 0)
            preview_text += f"  旋转: {rotation}°\n"
        
        self.config_preview.setPlainText(preview_text)
    
    def clear_template_details(self):
        """清空模板详情显示"""
        self.name_label.setText("未选择模板")
        self.time_label.setText("-")
        self.description_label.setText("-")
        self.config_preview.clear()
    
    def load_selected_template(self):
        """加载选中的模板"""
        current_item = self.template_list.currentItem()
        if current_item:
            template_data = current_item.data(Qt.UserRole)
            template_name = template_data["name"]
            
            # 发射加载信号
            self.template_loaded.emit(template_name)
            
            # 显示成功消息
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 已加载！")
            
            # 关闭对话框
            self.close()
    
    def delete_selected_template(self):
        """删除选中的模板"""
        current_item = self.template_list.currentItem()
        if current_item:
            template_data = current_item.data(Qt.UserRole)
            template_name = template_data["name"]
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除模板 '{template_name}' 吗？\n此操作无法撤销。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.config_manager.delete_template(template_name):
                    QMessageBox.information(self, "成功", f"模板 '{template_name}' 已删除！")
                    self.refresh_template_list()
                else:
                    QMessageBox.warning(self, "错误", f"删除模板 '{template_name}' 失败！")


class SaveTemplateDialog(QDialog):
    """保存模板对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_name = ""
        self.template_description = ""
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("保存水印模板")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("保存当前水印设置为模板")
        title_label.setFont(QFont("", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 模板名称
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("模板名称:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入模板名称...")
        self.name_input.textChanged.connect(self.validate_input)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # 模板描述
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("模板描述 (可选):"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("请输入模板描述...")
        self.desc_input.setMaximumHeight(80)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # 设置焦点
        self.name_input.setFocus()
    
    def validate_input(self):
        """验证输入"""
        name = self.name_input.text().strip()
        self.save_btn.setEnabled(len(name) > 0)
    
    def get_template_info(self):
        """获取模板信息"""
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.toPlainText().strip()
        }
