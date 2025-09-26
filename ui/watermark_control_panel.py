#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Watermark Control Panel
水印控制面板
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QSlider, QComboBox, QGroupBox,
                               QSpinBox, QPushButton, QTabWidget, QGridLayout,
                               QRadioButton, QButtonGroup, QFileDialog, QMessageBox,
                               QCheckBox, QColorDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QColor

from core.watermark import TextWatermark, ImageWatermark


class TextWatermarkPanel(QWidget):
    """文本水印控制面板"""
    
    # 信号定义
    watermark_changed = Signal()  # 水印参数改变
    
    def __init__(self):
        super().__init__()
        self.text_watermark = TextWatermark()
        self.init_ui()
        self.init_fonts()
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
        
        # 字体选择
        font_group = QGroupBox("字体设置")
        font_group.setFixedHeight(120)
        font_layout = QVBoxLayout(font_group)
        font_layout.setContentsMargins(8, 8, 8, 8)
        font_layout.setSpacing(4)
        
        # 字体家族选择
        family_layout = QHBoxLayout()
        family_layout.addWidget(QLabel("字体:"))
        
        self.font_combo = QComboBox()
        self.font_combo.setFixedWidth(150)
        # 字体列表将在初始化时填充
        family_layout.addWidget(self.font_combo)
        family_layout.addStretch()
        
        font_layout.addLayout(family_layout)
        
        # 字体样式选择
        style_layout = QHBoxLayout()
        
        self.bold_checkbox = QCheckBox("粗体")
        self.italic_checkbox = QCheckBox("斜体")
        
        style_layout.addWidget(self.bold_checkbox)
        style_layout.addWidget(self.italic_checkbox)
        style_layout.addStretch()
        
        font_layout.addLayout(style_layout)
        
        # 文字颜色
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色:"))
        
        self.color_button = QPushButton()
        self.color_button.setFixedSize(60, 24)
        self.color_button.setStyleSheet("background-color: rgb(255, 255, 255); border: 1px solid #999;")
        self.current_color = QColor(255, 255, 255)
        
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        font_layout.addLayout(color_layout)
        
        # 阴影效果
        shadow_group = QGroupBox("阴影效果")
        shadow_group.setFixedHeight(80)
        shadow_layout = QVBoxLayout(shadow_group)
        shadow_layout.setContentsMargins(8, 8, 8, 8)
        shadow_layout.setSpacing(4)
        
        # 启用阴影复选框
        self.shadow_checkbox = QCheckBox("启用阴影")
        shadow_layout.addWidget(self.shadow_checkbox)
        
        # 阴影参数
        shadow_params_layout = QHBoxLayout()
        
        shadow_params_layout.addWidget(QLabel("偏移:"))
        self.shadow_x_spinbox = QSpinBox()
        self.shadow_x_spinbox.setRange(-20, 20)
        self.shadow_x_spinbox.setValue(2)
        self.shadow_x_spinbox.setSuffix("px")
        self.shadow_x_spinbox.setFixedWidth(55)
        shadow_params_layout.addWidget(self.shadow_x_spinbox)
        
        self.shadow_y_spinbox = QSpinBox()
        self.shadow_y_spinbox.setRange(-20, 20)
        self.shadow_y_spinbox.setValue(2)
        self.shadow_y_spinbox.setSuffix("px")
        self.shadow_y_spinbox.setFixedWidth(55)
        shadow_params_layout.addWidget(self.shadow_y_spinbox)
        
        shadow_params_layout.addWidget(QLabel("颜色:"))
        self.shadow_color_button = QPushButton()
        self.shadow_color_button.setFixedSize(40, 20)
        self.shadow_color_button.setStyleSheet("background-color: rgb(0, 0, 0); border: 1px solid #999;")
        self.shadow_current_color = QColor(0, 0, 0)
        shadow_params_layout.addWidget(self.shadow_color_button)
        
        shadow_params_layout.addStretch()
        shadow_layout.addLayout(shadow_params_layout)
        
        # 描边效果
        stroke_group = QGroupBox("描边效果")
        stroke_group.setFixedHeight(80)
        stroke_layout = QVBoxLayout(stroke_group)
        stroke_layout.setContentsMargins(8, 8, 8, 8)
        stroke_layout.setSpacing(4)
        
        # 启用描边复选框
        self.stroke_checkbox = QCheckBox("启用描边")
        stroke_layout.addWidget(self.stroke_checkbox)
        
        # 描边参数
        stroke_params_layout = QHBoxLayout()
        
        stroke_params_layout.addWidget(QLabel("宽度:"))
        self.stroke_width_spinbox = QSpinBox()
        self.stroke_width_spinbox.setRange(1, 10)
        self.stroke_width_spinbox.setValue(2)
        self.stroke_width_spinbox.setSuffix("px")
        self.stroke_width_spinbox.setFixedWidth(60)
        stroke_params_layout.addWidget(self.stroke_width_spinbox)
        
        stroke_params_layout.addWidget(QLabel("颜色:"))
        self.stroke_color_button = QPushButton()
        self.stroke_color_button.setFixedSize(40, 20)
        self.stroke_color_button.setStyleSheet("background-color: rgb(0, 0, 0); border: 1px solid #999;")
        self.stroke_current_color = QColor(0, 0, 0)
        stroke_params_layout.addWidget(self.stroke_color_button)
        
        stroke_params_layout.addStretch()
        stroke_layout.addLayout(stroke_params_layout)
        
        # 不透明度
        opacity_group = QGroupBox("不透明度")
        opacity_group.setFixedHeight(60)
        opacity_layout = QHBoxLayout(opacity_group)
        opacity_layout.setContentsMargins(8, 8, 8, 8)
        
        opacity_layout.addWidget(QLabel("不透明度:"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(70)
        
        self.opacity_spinbox = QSpinBox()
        self.opacity_spinbox.setRange(0, 100)
        self.opacity_spinbox.setValue(70)
        self.opacity_spinbox.setSuffix("%")
        self.opacity_spinbox.setFixedWidth(60)
        
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spinbox)
        
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
        grid_widget = QWidget()
        grid_widget.setFixedSize(120, 80)
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(20, 10, 20, 10)
        
        self.position_buttons = QButtonGroup()
        positions = [
            (0, 0, (0.05, 0.05)),
            (0, 1, (0.5, 0.05)),
            (0, 2, (0.95, 0.05)),
            (1, 0, (0.05, 0.5)),
            (1, 1, (0.5, 0.5)),
            (1, 2, (0.95, 0.5)),
            (2, 0, (0.05, 0.95)),
            (2, 1, (0.5, 0.95)),
            (2, 2, (0.95, 0.95))
        ]
        
        for i, (row, col, pos) in enumerate(positions):
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setCheckable(True)
            btn.position = pos
            
            # 设置点状样式
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    background-color: #ddd;
                    border: 2px solid #999;
                }
                QPushButton:checked {
                    background-color: #2196f3;
                    border: 2px solid #1976d2;
                }
                QPushButton:hover {
                    background-color: #bbb;
                }
                QPushButton:checked:hover {
                    background-color: #1976d2;
                }
            """)
            
            self.position_buttons.addButton(btn, i)
            grid_layout.addWidget(btn, row, col)
            
            if i == 4:  # 默认选择中心
                btn.setChecked(True)
        
        # 将网格居中显示
        grid_container = QHBoxLayout()
        grid_container.addStretch()
        grid_container.addWidget(grid_widget)
        grid_container.addStretch()
        
        position_layout.addLayout(grid_container)
        
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
        layout.addWidget(font_group)
        layout.addWidget(shadow_group)
        layout.addWidget(stroke_group)
        layout.addWidget(opacity_group)
        layout.addWidget(position_group)
        layout.addWidget(rotation_group)
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def init_fonts(self):
        """初始化字体列表"""
        # 从水印对象获取可用字体
        fonts = self.text_watermark.get_available_fonts()
        self.font_combo.addItems(fonts)
        self.font_combo.setCurrentText("默认字体")
    
    def connect_signals(self):
        """连接信号槽"""
        # 文本改变
        self.text_input.textChanged.connect(self.on_text_changed)
        
        # 字体大小同步
        self.size_slider.valueChanged.connect(self.size_spinbox.setValue)
        self.size_spinbox.valueChanged.connect(self.size_slider.setValue)
        self.size_slider.valueChanged.connect(self.on_size_changed)
        
        # 字体选择
        self.font_combo.currentTextChanged.connect(self.on_font_family_changed)
        
        # 字体样式
        self.bold_checkbox.toggled.connect(self.on_font_style_changed)
        self.italic_checkbox.toggled.connect(self.on_font_style_changed)
        
        # 颜色选择
        self.color_button.clicked.connect(self.on_color_button_clicked)
        
        # 阴影效果
        self.shadow_checkbox.toggled.connect(self.on_shadow_settings_changed)
        self.shadow_x_spinbox.valueChanged.connect(self.on_shadow_settings_changed)
        self.shadow_y_spinbox.valueChanged.connect(self.on_shadow_settings_changed)
        self.shadow_color_button.clicked.connect(self.on_shadow_color_clicked)
        
        # 描边效果
        self.stroke_checkbox.toggled.connect(self.on_stroke_settings_changed)
        self.stroke_width_spinbox.valueChanged.connect(self.on_stroke_settings_changed)
        self.stroke_color_button.clicked.connect(self.on_stroke_color_clicked)
        
        # 不透明度同步
        self.opacity_slider.valueChanged.connect(self.opacity_spinbox.setValue)
        self.opacity_spinbox.valueChanged.connect(self.opacity_slider.setValue)
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
        # 更新字体列表以匹配文本内容
        self.update_font_list_for_text(text)
        self.watermark_changed.emit()
    
    def update_font_list_for_text(self, text: str):
        """根据文本内容更新字体列表"""
        # 检查是否包含中文
        contains_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
        
        # 获取适合的字体列表
        available_fonts = self.text_watermark.get_available_fonts(contains_chinese)
        
        # 保存当前选择
        current_font = self.font_combo.currentText()
        
        # 清空并重新填充字体列表
        self.font_combo.blockSignals(True)
        self.font_combo.clear()
        self.font_combo.addItems(available_fonts)
        
        # 尝试恢复之前的选择，如果不在新列表中则选择默认字体
        if current_font in available_fonts:
            self.font_combo.setCurrentText(current_font)
        else:
            self.font_combo.setCurrentText("默认字体")
            # 如果字体改变了，需要更新水印对象
            self.text_watermark.set_font_family("默认字体")
        
        self.font_combo.blockSignals(False)
    
    def on_size_changed(self, size: int):
        """字体大小改变事件"""
        self.text_watermark.set_font_size(size)
        self.watermark_changed.emit()
    
    def on_font_family_changed(self, font_family: str):
        """字体家族改变事件"""
        self.text_watermark.set_font_family(font_family)
        self.watermark_changed.emit()
    
    def on_font_style_changed(self):
        """字体样式改变事件"""
        bold = self.bold_checkbox.isChecked()
        italic = self.italic_checkbox.isChecked()
        self.text_watermark.set_font_style(bold=bold, italic=italic)
        self.watermark_changed.emit()
    
    def on_color_button_clicked(self):
        """颜色按钮点击事件"""
        color = QColorDialog.getColor(self.current_color, self, "选择文字颜色")
        if color.isValid():
            self.current_color = color
            # 更新按钮颜色
            self.color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"border: 1px solid #999;"
            )
            # 更新水印颜色（保持当前透明度）
            current_alpha = self.text_watermark.font_color[3]
            new_color = (color.red(), color.green(), color.blue(), current_alpha)
            self.text_watermark.font_color = new_color
            self.watermark_changed.emit()
    
    def on_shadow_settings_changed(self):
        """阴影设置改变事件"""
        enabled = self.shadow_checkbox.isChecked()
        offset = (self.shadow_x_spinbox.value(), self.shadow_y_spinbox.value())
        # 使用当前阴影颜色，包含透明度
        color = (*self.shadow_current_color.getRgb()[:3], 128)  # 固定透明度为128
        self.text_watermark.set_shadow(enabled, offset, color)
        self.watermark_changed.emit()
    
    def on_shadow_color_clicked(self):
        """阴影颜色按钮点击事件"""
        color = QColorDialog.getColor(self.shadow_current_color, self, "选择阴影颜色")
        if color.isValid():
            self.shadow_current_color = color
            self.shadow_color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"border: 1px solid #999;"
            )
            # 更新阴影设置
            self.on_shadow_settings_changed()
    
    def on_stroke_settings_changed(self):
        """描边设置改变事件"""
        enabled = self.stroke_checkbox.isChecked()
        width = self.stroke_width_spinbox.value()
        # 使用当前描边颜色，完全不透明
        color = (*self.stroke_current_color.getRgb()[:3], 255)
        self.text_watermark.set_stroke(enabled, width, color)
        self.watermark_changed.emit()
    
    def on_stroke_color_clicked(self):
        """描边颜色按钮点击事件"""
        color = QColorDialog.getColor(self.stroke_current_color, self, "选择描边颜色")
        if color.isValid():
            self.stroke_current_color = color
            self.stroke_color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); "
                f"border: 1px solid #999;"
            )
            # 更新描边设置
            self.on_stroke_settings_changed()
    
    def on_opacity_changed(self, value: int):
        """不透明度改变事件"""
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
        self.font_combo.setCurrentText("默认字体")
        self.bold_checkbox.setChecked(False)
        self.italic_checkbox.setChecked(False)
        self.current_color = QColor(255, 255, 255)
        self.color_button.setStyleSheet("background-color: rgb(255, 255, 255); border: 1px solid #999;")
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
        self.font_combo.blockSignals(True)
        self.bold_checkbox.blockSignals(True)
        self.italic_checkbox.blockSignals(True)
        self.opacity_slider.blockSignals(True)
        self.opacity_spinbox.blockSignals(True)
        self.x_spinbox.blockSignals(True)
        self.y_spinbox.blockSignals(True)
        self.rotation_slider.blockSignals(True)
        
        try:
            # 更新UI控件值
            self.text_input.setText(self.text_watermark.text)
            self.size_slider.setValue(self.text_watermark.font_size)
            
            # 更新字体设置
            self.font_combo.setCurrentText(self.text_watermark.font_family)
            self.bold_checkbox.setChecked(self.text_watermark.font_bold)
            self.italic_checkbox.setChecked(self.text_watermark.font_italic)
            
            # 更新颜色按钮
            r, g, b, a = self.text_watermark.font_color
            self.current_color = QColor(r, g, b)
            self.color_button.setStyleSheet(
                f"background-color: rgb({r}, {g}, {b}); border: 1px solid #999;"
            )
            
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
            self.font_combo.blockSignals(False)
            self.bold_checkbox.blockSignals(False)
            self.italic_checkbox.blockSignals(False)
            self.opacity_slider.blockSignals(False)
            self.opacity_spinbox.blockSignals(False)
            self.x_spinbox.blockSignals(False)
            self.y_spinbox.blockSignals(False)
            self.rotation_slider.blockSignals(False)


class ImageWatermarkPanel(QWidget):
    """图片水印控制面板"""
    
    # 信号定义
    watermark_changed = Signal()  # 水印参数改变
    
    def __init__(self):
        super().__init__()
        self.image_watermark = ImageWatermark()
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 图片选择
        image_group = QGroupBox("水印图片")
        image_group.setFixedHeight(80)
        image_layout = QVBoxLayout(image_group)
        image_layout.setContentsMargins(8, 8, 8, 8)
        
        # 文件选择按钮和预览
        file_layout = QHBoxLayout()
        
        self.select_button = QPushButton("选择图片...")
        self.select_button.setFixedHeight(24)
        
        self.preview_label = QLabel("未选择图片")
        self.preview_label.setStyleSheet("color: #666; font-size: 11px;")
        self.preview_label.setWordWrap(True)
        
        file_layout.addWidget(self.select_button)
        file_layout.addWidget(self.preview_label)
        file_layout.addStretch()
        
        image_layout.addLayout(file_layout)
        
        # 缩放
        scale_group = QGroupBox("缩放")
        scale_group.setFixedHeight(60)
        scale_layout = QHBoxLayout(scale_group)
        scale_layout.setContentsMargins(8, 8, 8, 8)
        
        scale_layout.addWidget(QLabel("大小:"))
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 500)  # 0.1x 到 5.0x
        self.scale_slider.setValue(100)  # 1.0x
        
        self.scale_spinbox = QSpinBox()
        self.scale_spinbox.setRange(10, 500)
        self.scale_spinbox.setValue(100)
        self.scale_spinbox.setSuffix("%")
        self.scale_spinbox.setFixedWidth(70)
        
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_spinbox)
        
        # 不透明度
        opacity_group = QGroupBox("不透明度")
        opacity_group.setFixedHeight(60)
        opacity_layout = QHBoxLayout(opacity_group)
        opacity_layout.setContentsMargins(8, 8, 8, 8)
        
        opacity_layout.addWidget(QLabel("不透明度:"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(70)
        
        self.opacity_spinbox = QSpinBox()
        self.opacity_spinbox.setRange(0, 100)
        self.opacity_spinbox.setValue(70)
        self.opacity_spinbox.setSuffix("%")
        self.opacity_spinbox.setFixedWidth(60)
        
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_spinbox)
        
        # 位置设置（复用文本水印的九宫格逻辑）
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
        grid_widget = QWidget()
        grid_widget.setFixedSize(120, 80)
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(20, 10, 20, 10)
        
        self.position_buttons = QButtonGroup()
        positions = [
            (0, 0, (0.05, 0.05)),
            (0, 1, (0.5, 0.05)),
            (0, 2, (0.95, 0.05)),
            (1, 0, (0.05, 0.5)),
            (1, 1, (0.5, 0.5)),
            (1, 2, (0.95, 0.5)),
            (2, 0, (0.05, 0.95)),
            (2, 1, (0.5, 0.95)),
            (2, 2, (0.95, 0.95))
        ]
        
        for i, (row, col, pos) in enumerate(positions):
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setCheckable(True)
            btn.position = pos
            
            # 设置点状样式
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    background-color: #ddd;
                    border: 2px solid #999;
                }
                QPushButton:checked {
                    background-color: #2196f3;
                    border: 2px solid #1976d2;
                }
                QPushButton:hover {
                    background-color: #bbb;
                }
                QPushButton:checked:hover {
                    background-color: #1976d2;
                }
            """)
            
            self.position_buttons.addButton(btn, i)
            grid_layout.addWidget(btn, row, col)
            
            if i == 4:  # 默认选择中心
                btn.setChecked(True)
        
        # 将网格居中显示
        grid_container = QHBoxLayout()
        grid_container.addStretch()
        grid_container.addWidget(grid_widget)
        grid_container.addStretch()
        
        position_layout.addLayout(grid_container)
        
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
        
        self.clear_button = QPushButton("清除图片")
        self.clear_button.setFixedWidth(80)
        self.clear_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        
        # 添加到主布局
        layout.addWidget(image_group)
        layout.addWidget(scale_group)
        layout.addWidget(opacity_group)
        layout.addWidget(position_group)
        layout.addWidget(rotation_group)
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def connect_signals(self):
        """连接信号槽"""
        # 图片选择
        self.select_button.clicked.connect(self.select_watermark_image)
        
        # 缩放同步
        self.scale_slider.valueChanged.connect(self.scale_spinbox.setValue)
        self.scale_spinbox.valueChanged.connect(self.scale_slider.setValue)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        
        # 不透明度同步
        self.opacity_slider.valueChanged.connect(self.opacity_spinbox.setValue)
        self.opacity_spinbox.valueChanged.connect(self.opacity_slider.setValue)
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
        
        # 清除按钮
        self.clear_button.clicked.connect(self.clear_watermark_image)
    
    def select_watermark_image(self):
        """选择水印图片"""
        file_filter = "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.gif);;PNG 图片 (*.png);;所有文件 (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择水印图片", "", file_filter
        )
        
        if file_path:
            if self.image_watermark.load_watermark_image(file_path):
                import os
                filename = os.path.basename(file_path)
                self.preview_label.setText(f"已选择: {filename}")
                self.clear_button.setEnabled(True)
                self.watermark_changed.emit()
            else:
                QMessageBox.warning(self, "错误", "无法加载选择的图片文件")
    
    def clear_watermark_image(self):
        """清除水印图片"""
        self.image_watermark = ImageWatermark()
        self.preview_label.setText("未选择图片")
        self.clear_button.setEnabled(False)
        self.watermark_changed.emit()
    
    def on_scale_changed(self, value: int):
        """缩放改变事件"""
        scale = value / 100.0  # 转换为0.1-5.0的比例
        self.image_watermark.set_scale(scale)
        self.watermark_changed.emit()
    
    def on_opacity_changed(self, value: int):
        """不透明度改变事件"""
        self.image_watermark.set_transparency(value)
        self.watermark_changed.emit()
    
    def on_position_mode_changed(self):
        """位置模式改变事件"""
        self.update_position_mode()
    
    def on_position_button_clicked(self, button):
        """九宫格位置按钮点击事件"""
        if self.preset_mode_radio.isChecked():
            x, y = button.position
            self.image_watermark.set_position(x, y)
            
            # 同步到自定义位置显示
            self.x_spinbox.setValue(int(x * 100))
            self.y_spinbox.setValue(int(y * 100))
            
            self.watermark_changed.emit()
    
    def on_custom_position_changed(self):
        """自定义位置改变事件"""
        if self.custom_mode_radio.isChecked():
            x = self.x_spinbox.value() / 100.0
            y = self.y_spinbox.value() / 100.0
            self.image_watermark.set_position(x, y)
            
            # 清空九宫格选择
            for button in self.position_buttons.buttons():
                button.setChecked(False)
            
            self.watermark_changed.emit()
    
    def on_rotation_changed(self, angle: int):
        """旋转角度改变事件"""
        self.image_watermark.set_rotation(angle)
        self.watermark_changed.emit()
    
    def update_position_mode(self):
        """更新位置模式显示"""
        is_preset = self.preset_mode_radio.isChecked()
        
        # 启用/禁用对应控件
        for button in self.position_buttons.buttons():
            button.setEnabled(is_preset)
        
        self.x_spinbox.setEnabled(not is_preset)
        self.y_spinbox.setEnabled(not is_preset)
    
    def get_watermark(self) -> ImageWatermark:
        """获取当前水印对象
        
        Returns:
            ImageWatermark: 图片水印对象
        """
        return self.image_watermark if self.image_watermark.watermark_image is not None else None


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
        
        # 图片水印标签页
        self.image_panel = ImageWatermarkPanel()
        self.tab_widget.addTab(self.image_panel, "图片水印")
        
        layout.addWidget(self.tab_widget)
    
    def connect_signals(self):
        """连接信号槽"""
        self.text_panel.watermark_changed.connect(self.watermark_changed)
        self.image_panel.watermark_changed.connect(self.watermark_changed)
        
        # 选项卡切换时也发出信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 初始化时触发一次信号
        self.watermark_changed.emit()
    
    def on_tab_changed(self, index):
        """选项卡切换事件"""
        self.watermark_changed.emit()
    
    def get_current_watermark(self):
        """获取当前激活的水印对象
        
        Returns:
            水印对象或None
        """
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:  # 文本水印
            return self.text_panel.get_watermark()
        else:  # 图片水印
            return self.image_panel.get_watermark()
    
    def get_watermark_type(self) -> str:
        """获取当前水印类型
        
        Returns:
            str: 'text' 或 'image'
        """
        current_index = self.tab_widget.currentIndex()
        return 'text' if current_index == 0 else 'image'
