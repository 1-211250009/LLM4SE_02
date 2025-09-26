#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2 - Export Dialog
导出对话框
"""

import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QComboBox, QGroupBox,
                               QRadioButton, QButtonGroup, QSlider, QSpinBox,
                               QFileDialog, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QIntValidator

from core.file_manager import FileManager
from core.image_processor import ImageProcessor


class ExportWorker(QThread):
    """导出工作线程"""
    progress_updated = Signal(int, int, str)  # current, total, filename
    export_finished = Signal(int, int)  # success_count, total_count
    
    def __init__(self, file_manager: FileManager, export_options: dict):
        super().__init__()
        self.file_manager = file_manager
        self.export_options = export_options
        self.image_processor = ImageProcessor()
        self.should_stop = False
    
    def run(self):
        """执行导出任务"""
        # 只导出选中的图片
        images = self.file_manager.get_selected_images()
        total = len(images)
        success_count = 0
        
        for i, img_info in enumerate(images):
            if self.should_stop:
                break
            
            try:
                filename = img_info['filename']
                self.progress_updated.emit(i + 1, total, filename)
                
                # 加载原图
                image = self.image_processor.load_image(img_info['path'])
                if image is None:
                    continue
                
                # 生成输出文件名
                output_path = self.image_processor.generate_output_filename(
                    img_info['path'],
                    self.export_options['output_dir'],
                    self.export_options['naming_rule'],
                    self.export_options['prefix'],
                    self.export_options['suffix'],
                    self.export_options['format']
                )
                
                # 调整图片尺寸（如果需要）
                if self.export_options['resize_enabled']:
                    image = self._resize_image(image, self.export_options)
                
                # 保存图片
                if self.image_processor.save_image(
                    image, 
                    output_path,
                    self.export_options['format'],
                    self.export_options['quality']
                ):
                    success_count += 1
                
            except Exception as e:
                print(f"导出图片失败 {img_info['path']}: {e}")
        
        self.export_finished.emit(success_count, total)
    
    def _resize_image(self, image, options):
        """调整图片尺寸"""
        if options['resize_mode'] == 'percentage':
            # 按百分比缩放
            scale = options['resize_percentage'] / 100.0
            new_size = (int(image.width * scale), int(image.height * scale))
        elif options['resize_mode'] == 'width':
            # 按宽度缩放
            new_width = options['resize_width']
            scale = new_width / image.width
            new_size = (new_width, int(image.height * scale))
        elif options['resize_mode'] == 'height':
            # 按高度缩放
            new_height = options['resize_height']
            scale = new_height / image.height
            new_size = (int(image.width * scale), new_height)
        else:
            return image
        
        # 使用高质量重采样
        from PIL import Image
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def stop(self):
        """停止导出"""
        self.should_stop = True


class ExportDialog(QDialog):
    """导出对话框"""
    
    def __init__(self, file_manager: FileManager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.export_worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("导出图片")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 输出目录选择
        dir_group = QGroupBox("输出目录")
        dir_layout = QHBoxLayout(dir_group)
        
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("选择输出目录...")
        self.dir_edit.setReadOnly(True)
        
        dir_browse_btn = QPushButton("浏览...")
        dir_browse_btn.clicked.connect(self.browse_output_dir)
        
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(dir_browse_btn)
        
        # 命名规则
        naming_group = QGroupBox("文件命名")
        naming_layout = QVBoxLayout(naming_group)
        
        self.naming_group = QButtonGroup()
        
        self.original_radio = QRadioButton("保留原文件名")
        self.original_radio.setChecked(True)
        
        prefix_layout = QHBoxLayout()
        self.prefix_radio = QRadioButton("添加前缀:")
        self.prefix_edit = QLineEdit("wm_")
        self.prefix_edit.setMaximumWidth(100)
        prefix_layout.addWidget(self.prefix_radio)
        prefix_layout.addWidget(self.prefix_edit)
        prefix_layout.addStretch()
        
        suffix_layout = QHBoxLayout()
        self.suffix_radio = QRadioButton("添加后缀:")
        self.suffix_edit = QLineEdit("_watermarked")
        self.suffix_edit.setMaximumWidth(150)
        suffix_layout.addWidget(self.suffix_radio)
        suffix_layout.addWidget(self.suffix_edit)
        suffix_layout.addStretch()
        
        self.naming_group.addButton(self.original_radio, 0)
        self.naming_group.addButton(self.prefix_radio, 1)
        self.naming_group.addButton(self.suffix_radio, 2)
        
        naming_layout.addWidget(self.original_radio)
        naming_layout.addLayout(prefix_layout)
        naming_layout.addLayout(suffix_layout)
        
        # 输出格式
        format_group = QGroupBox("输出格式")
        format_layout = QHBoxLayout(format_group)
        
        format_layout.addWidget(QLabel("格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        
        # JPEG质量设置
        quality_layout = QHBoxLayout()
        self.quality_label = QLabel("JPEG质量:")
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_value_label = QLabel("95")
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_value_label.setText(str(v))
        )
        
        quality_layout.addWidget(self.quality_label)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_value_label)
        
        format_layout.addLayout(quality_layout)
        
        # 尺寸调整（高级功能）
        resize_group = QGroupBox("尺寸调整 (可选)")
        resize_layout = QVBoxLayout(resize_group)
        
        self.resize_enabled = QRadioButton("不调整尺寸")
        self.resize_enabled.setChecked(True)
        
        # 按百分比
        percent_layout = QHBoxLayout()
        self.resize_percent = QRadioButton("按百分比缩放:")
        self.percent_spin = QSpinBox()
        self.percent_spin.setRange(10, 200)
        self.percent_spin.setValue(100)
        self.percent_spin.setSuffix("%")
        percent_layout.addWidget(self.resize_percent)
        percent_layout.addWidget(self.percent_spin)
        percent_layout.addStretch()
        
        # 按宽度
        width_layout = QHBoxLayout()
        self.resize_width = QRadioButton("按宽度:")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 10000)
        self.width_spin.setValue(1920)
        self.width_spin.setSuffix("px")
        width_layout.addWidget(self.resize_width)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        
        # 按高度
        height_layout = QHBoxLayout()
        self.resize_height = QRadioButton("按高度:")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 10000)
        self.height_spin.setValue(1080)
        self.height_spin.setSuffix("px")
        height_layout.addWidget(self.resize_height)
        height_layout.addWidget(self.height_spin)
        height_layout.addStretch()
        
        self.resize_group = QButtonGroup()
        self.resize_group.addButton(self.resize_enabled, 0)
        self.resize_group.addButton(self.resize_percent, 1)
        self.resize_group.addButton(self.resize_width, 2)
        self.resize_group.addButton(self.resize_height, 3)
        
        resize_layout.addWidget(self.resize_enabled)
        resize_layout.addLayout(percent_layout)
        resize_layout.addLayout(width_layout)
        resize_layout.addLayout(height_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("开始导出")
        self.export_btn.clicked.connect(self.start_export)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # 添加到主布局
        layout.addWidget(dir_group)
        layout.addWidget(naming_group)
        layout.addWidget(format_group)
        layout.addWidget(resize_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        layout.addLayout(button_layout)
        
        # 初始状态
        self.on_format_changed("JPEG")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.dir_edit.setText(dir_path)
    
    def on_format_changed(self, format_name):
        """格式改变事件"""
        is_jpeg = format_name == "JPEG"
        self.quality_label.setVisible(is_jpeg)
        self.quality_slider.setVisible(is_jpeg)
        self.quality_value_label.setVisible(is_jpeg)
    
    def get_export_options(self) -> dict:
        """获取导出选项"""
        # 命名规则
        naming_rule = "original"
        prefix = ""
        suffix = ""
        
        if self.prefix_radio.isChecked():
            naming_rule = "prefix"
            prefix = self.prefix_edit.text()
        elif self.suffix_radio.isChecked():
            naming_rule = "suffix"
            suffix = self.suffix_edit.text()
        
        # 尺寸调整
        resize_enabled = not self.resize_enabled.isChecked()
        resize_mode = ""
        resize_percentage = 100
        resize_width = 1920
        resize_height = 1080
        
        if self.resize_percent.isChecked():
            resize_mode = "percentage"
            resize_percentage = self.percent_spin.value()
        elif self.resize_width.isChecked():
            resize_mode = "width"
            resize_width = self.width_spin.value()
        elif self.resize_height.isChecked():
            resize_mode = "height"
            resize_height = self.height_spin.value()
        
        return {
            'output_dir': self.dir_edit.text(),
            'naming_rule': naming_rule,
            'prefix': prefix,
            'suffix': suffix,
            'format': self.format_combo.currentText(),
            'quality': self.quality_slider.value(),
            'resize_enabled': resize_enabled,
            'resize_mode': resize_mode,
            'resize_percentage': resize_percentage,
            'resize_width': resize_width,
            'resize_height': resize_height
        }
    
    def start_export(self):
        """开始导出"""
        if self.file_manager.get_selected_count() == 0:
            QMessageBox.warning(self, "警告", "请先选择要导出的图片")
            return
        
        options = self.get_export_options()
        
        # 验证输出目录
        if not options['output_dir']:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return
        
        is_valid, error_msg = self.file_manager.validate_output_directory(options['output_dir'])
        if not is_valid:
            QMessageBox.warning(self, "警告", error_msg)
            return
        
        # 验证命名参数
        if options['naming_rule'] == 'prefix' and not options['prefix']:
            QMessageBox.warning(self, "警告", "请输入前缀")
            return
        elif options['naming_rule'] == 'suffix' and not options['suffix']:
            QMessageBox.warning(self, "警告", "请输入后缀")
            return
        
        # 开始导出
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setMaximum(self.file_manager.get_selected_count())
        
        self.export_worker = ExportWorker(self.file_manager, options)
        self.export_worker.progress_updated.connect(self.on_progress_updated)
        self.export_worker.export_finished.connect(self.on_export_finished)
        self.export_worker.start()
    
    def on_progress_updated(self, current: int, total: int, filename: str):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"正在导出: {filename} ({current}/{total})")
    
    def on_export_finished(self, success_count: int, total_count: int):
        """导出完成"""
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        if success_count == total_count:
            QMessageBox.information(self, "导出完成", 
                f"成功导出 {success_count} 张图片")
        else:
            QMessageBox.warning(self, "导出完成", 
                f"成功导出 {success_count}/{total_count} 张图片")
        
        self.accept()
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.export_worker and self.export_worker.isRunning():
            self.export_worker.stop()
            self.export_worker.wait()
        event.accept()
