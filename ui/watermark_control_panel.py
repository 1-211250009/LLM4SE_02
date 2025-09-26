#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Watermark Control Panel
水印控制面板
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QSlider, QComboBox, QGroupBox,
                               QSpinBox, QPushButton, QTabWidget, QGridLayout,
                               QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.watermark import TextWatermark


class TextWatermarkPanel(QWidget):
    """文本水印控制面板"""
    
    # 信号定义
    watermark_changed = Signal()  # 水印参数改变
    
    def __init__(self):
        super().__init__()
        self.text_watermark = TextWatermark()
        self.init_ui()
        self.connect_signals()
        
        # 初始化默认值到控件（确保水印对象和UI同步）
        self.update_ui_from_watermark()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 文本输入
        text_group = QGroupBox("水印文本")
        text_group.setFixedHeight(60)
        text_layout = QVBoxLayout(text_group)
        text_layout.setContentsMargins(8, 8, 8, 8)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("请输入水印文本...")
        self.text_input.setText("Photo Watermark")
        self.text_input.setFixedHeight(24)
        text_layout.addWidget(self.text_input)
        
        # 字体大小
        size_group = QGroupBox("字体大小")
        size_group.setFixedHeight(60)
        size_layout = QHBoxLayout(size_group)
        size_layout.setContentsMargins(8, 8, 8, 8)
        
        size_layout.addWidget(QLabel("大小:"))
        
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 200)
        self.size_slider.setValue(24)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(10, 200)
        self.size_spinbox.setValue(24)
        self.size_spinbox.setSuffix("px")
        
        size_layout.addWidget(self.size_slider)
        size_layout.addWidget(self.size_spinbox)
        
        # 不透明度
        opacity_group = QGroupBox("不透明度")
        opacity_group.setFixedHeight(60)
        opacity_layout = QHBoxLayout(opacity_group)
        opacity_layout.setContentsMargins(8, 8, 8, 8)
        
        opacity_layout.addWidget(QLabel("不透明度:"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(70)
        
        self.opacity_label = QLabel("70%")
        self.opacity_label.setMinimumWidth(40)
        
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        # 位置设置
        position_group = QGroupBox("水印位置")
        position_group.setFixedHeight(160)
        position_layout = QVBoxLayout(position_group)
        position_layout.setContentsMargins(8, 8, 8, 8)
        position_layout.setSpacing(4)
        
        # 位置模式选择
        self.position_mode_group = QButtonGroup()
        
        mode_layout = QHBoxLayout()
        self.preset_mode_radio = QRadioButton("预设位置")
        self.preset_mode_radio.setChecked(True)
        self.custom_mode_radio = QRadioButton("自定义位置")
        
        self.position_mode_group.addButton(self.preset_mode_radio, 0)
        self.position_mode_group.addButton(self.custom_mode_radio, 1)
        
        mode_layout.addWidget(self.preset_mode_radio)
        mode_layout.addWidget(self.custom_mode_radio)
        mode_layout.addStretch()
        
        position_layout.addLayout(mode_layout)
        
        # 九宫格位置选择
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)
        
        self.position_buttons = QButtonGroup()
        positions = [
            ("左上", 0, 0, (0.05, 0.05)),
            ("上中", 0, 1, (0.5, 0.05)),
            ("右上", 0, 2, (0.95, 0.05)),
            ("左中", 1, 0, (0.05, 0.5)),
            ("中心", 1, 1, (0.5, 0.5)),
            ("右中", 1, 2, (0.95, 0.5)),
            ("左下", 2, 0, (0.05, 0.95)),
            ("下中", 2, 1, (0.5, 0.95)),
            ("右下", 2, 2, (0.95, 0.95))
        ]
        
        for i, (name, row, col, pos) in enumerate(positions):
            btn = QPushButton(name)
            btn.setFixedSize(50, 25)
            btn.setCheckable(True)
            btn.position = pos
            self.position_buttons.addButton(btn, i)
            grid_layout.addWidget(btn, row, col)
            
            if i == 4:  # 默认选择中心
                btn.setChecked(True)
        
        position_layout.addLayout(grid_layout)
        
        # 自定义位置调整
        custom_layout = QHBoxLayout()
        
        custom_layout.addWidget(QLabel("X:"))
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(0, 100)
        self.x_spinbox.setValue(50)
        self.x_spinbox.setSuffix("%")
        self.x_spinbox.setFixedWidth(60)
        custom_layout.addWidget(self.x_spinbox)
        
        custom_layout.addWidget(QLabel("Y:"))
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(0, 100)
        self.y_spinbox.setValue(50)
        self.y_spinbox.setSuffix("%")
        self.y_spinbox.setFixedWidth(60)
        custom_layout.addWidget(self.y_spinbox)
        
        custom_layout.addStretch()
        
        position_layout.addLayout(custom_layout)
        
        # 初始状态设置
        self.update_position_mode()
        
        # 旋转角度
        rotation_group = QGroupBox("旋转角度")
        rotation_group.setFixedHeight(60)
        rotation_layout = QHBoxLayout(rotation_group)
        rotation_layout.setContentsMargins(8, 8, 8, 8)
        
        rotation_layout.addWidget(QLabel("角度:"))
        
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(-180, 180)
        self.rotation_slider.setValue(0)
        
        self.rotation_spinbox = QSpinBox()
        self.rotation_spinbox.setRange(-180, 180)
        self.rotation_spinbox.setValue(0)
        self.rotation_spinbox.setSuffix("°")
        
        rotation_layout.addWidget(self.rotation_slider)
        rotation_layout.addWidget(self.rotation_spinbox)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("重置")
        self.reset_button.setFixedWidth(80)
        
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        
        # 添加到主布局
        layout.addWidget(text_group)
        layout.addWidget(size_group)
        layout.addWidget(opacity_group)
        layout.addWidget(position_group)
        layout.addWidget(rotation_group)
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def connect_signals(self):
        """连接信号槽"""
        # 文本改变
        self.text_input.textChanged.connect(self.on_text_changed)
        
        # 字体大小同步
        self.size_slider.valueChanged.connect(self.size_spinbox.setValue)
        self.size_spinbox.valueChanged.connect(self.size_slider.setValue)
        self.size_slider.valueChanged.connect(self.on_size_changed)
        
        # 不透明度
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        
        # 位置模式
        self.position_mode_group.buttonClicked.connect(self.on_position_mode_changed)
        
        # 位置按钮
        self.position_buttons.buttonClicked.connect(self.on_position_button_clicked)
        
        # 自定义位置
        self.x_spinbox.valueChanged.connect(self.on_custom_position_changed)
        self.y_spinbox.valueChanged.connect(self.on_custom_position_changed)
        
        # 旋转角度同步
        self.rotation_slider.valueChanged.connect(self.rotation_spinbox.setValue)
        self.rotation_spinbox.valueChanged.connect(self.rotation_slider.setValue)
        self.rotation_slider.valueChanged.connect(self.on_rotation_changed)
        
        # 重置按钮
        self.reset_button.clicked.connect(self.reset_watermark)
    
    def on_text_changed(self, text: str):
        """文本改变事件"""
        self.text_watermark.set_text(text)
        self.watermark_changed.emit()
    
    def on_size_changed(self, size: int):
        """字体大小改变事件"""
        self.text_watermark.set_font_size(size)
        self.watermark_changed.emit()
    
    def on_opacity_changed(self, value: int):
        """不透明度改变事件"""
        self.opacity_label.setText(f"{value}%")
        self.text_watermark.set_transparency(value)  # 现在value就是不透明度
        self.watermark_changed.emit()
    
    def on_position_mode_changed(self):
        """位置模式改变事件"""
        self.update_position_mode()
    
    def on_position_button_clicked(self, button):
        """九宫格位置按钮点击事件"""
        if self.preset_mode_radio.isChecked():
            x, y = button.position
            self.text_watermark.set_position(x, y)
            
            # 同步到自定义位置显示
            self.x_spinbox.setValue(int(x * 100))
            self.y_spinbox.setValue(int(y * 100))
            
            self.watermark_changed.emit()
    
    def on_custom_position_changed(self):
        """自定义位置改变事件"""
        if self.custom_mode_radio.isChecked():
            x = self.x_spinbox.value() / 100.0
            y = self.y_spinbox.value() / 100.0
            self.text_watermark.set_position(x, y)
            
            # 清空九宫格选择
            for button in self.position_buttons.buttons():
                button.setChecked(False)
            
            self.watermark_changed.emit()
    
    def update_position_mode(self):
        """更新位置模式显示"""
        is_preset = self.preset_mode_radio.isChecked()
        
        # 启用/禁用对应控件
        for button in self.position_buttons.buttons():
            button.setEnabled(is_preset)
        
        self.x_spinbox.setEnabled(not is_preset)
        self.y_spinbox.setEnabled(not is_preset)
    
    def on_rotation_changed(self, angle: int):
        """旋转角度改变事件"""
        self.text_watermark.set_rotation(angle)
        self.watermark_changed.emit()
    
    def reset_watermark(self):
        """重置水印设置"""
        # 重置到默认值
        self.text_input.setText("Photo Watermark")
        self.size_slider.setValue(24)
        self.opacity_slider.setValue(70)
        self.preset_mode_radio.setChecked(True)
        self.position_buttons.button(4).setChecked(True)  # 选择中心位置
        self.rotation_slider.setValue(0)
        
        # 重置水印对象
        self.text_watermark = TextWatermark()
        self.text_watermark.set_transparency(70)
        
        self.update_position_mode()
        self.watermark_changed.emit()
    
    def get_watermark(self) -> TextWatermark:
        """获取当前水印对象
        
        Returns:
            TextWatermark: 文本水印对象
        """
        return self.text_watermark
    
    def update_ui_from_watermark(self):
        """从水印对象更新UI控件"""
        # 暂时断开信号连接，避免循环触发
        self.text_input.blockSignals(True)
        self.size_slider.blockSignals(True)
        self.opacity_slider.blockSignals(True)
        self.x_spinbox.blockSignals(True)
        self.y_spinbox.blockSignals(True)
        self.rotation_slider.blockSignals(True)
        
        try:
            # 更新UI控件值
            self.text_input.setText(self.text_watermark.text)
            self.size_slider.setValue(self.text_watermark.font_size)
            
            # 计算不透明度百分比（直接使用透明度值）
            opacity = int(self.text_watermark.font_color[3] * 100 / 255)
            self.opacity_slider.setValue(opacity)
            
            # 更新位置
            x, y = self.text_watermark.position
            self.x_spinbox.setValue(int(x * 100))
            self.y_spinbox.setValue(int(y * 100))
            
            # 更新旋转角度
            self.rotation_slider.setValue(int(self.text_watermark.rotation))
            
            # 选中对应的九宫格按钮
            for i, button in enumerate(self.position_buttons.buttons()):
                if abs(button.position[0] - x) < 0.01 and abs(button.position[1] - y) < 0.01:
                    button.setChecked(True)
                    break
            
        finally:
            # 恢复信号连接
            self.text_input.blockSignals(False)
            self.size_slider.blockSignals(False)
            self.opacity_slider.blockSignals(False)
            self.x_spinbox.blockSignals(False)
            self.y_spinbox.blockSignals(False)
            self.rotation_slider.blockSignals(False)


class WatermarkControlPanel(QWidget):
    """水印控制面板主组件"""
    
    # 信号定义
    watermark_changed = Signal()  # 水印参数改变
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 文本水印标签页
        self.text_panel = TextWatermarkPanel()
        self.tab_widget.addTab(self.text_panel, "文本水印")
        
        # 图片水印标签页（暂时占位）
        image_placeholder = QWidget()
        image_layout = QVBoxLayout(image_placeholder)
        placeholder_label = QLabel("图片水印功能将在阶段3实现")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("color: #666; font-size: 14px;")
        image_layout.addWidget(placeholder_label)
        
        self.tab_widget.addTab(image_placeholder, "图片水印")
        
        layout.addWidget(self.tab_widget)
    
    def connect_signals(self):
        """连接信号槽"""
        self.text_panel.watermark_changed.connect(self.watermark_changed)
    
    def get_current_watermark(self):
        """获取当前激活的水印对象
        
        Returns:
            水印对象或None
        """
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:  # 文本水印
            return self.text_panel.get_watermark()
        else:  # 图片水印（暂未实现）
            return None
    
    def get_watermark_type(self) -> str:
        """获取当前水印类型
        
        Returns:
            str: 'text' 或 'image'
        """
        current_index = self.tab_widget.currentIndex()
        return 'text' if current_index == 0 else 'image'
