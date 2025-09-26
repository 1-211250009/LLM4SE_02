#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark 2
水印文件本地应用（MacOS）

主程序入口
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """主程序入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("Photo Watermark 2")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LLM4SE")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
