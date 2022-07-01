# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# Copyright (c) Peter Harrison 2022
# License: MIT
# description: A Maze Editor written using PyQt5
# python version >= 3.8
# ============================================================================ #


import os
import sys
from pathlib import Path
# This is a sample Python script.
from PyQt5.QtCore import Qt, QT_VERSION_STR
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow

# this may or may not help with high DPI screen
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

version = list(map(int, QT_VERSION_STR.split('.')))

if version[1] >= 14:
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("PyQt Micromouse Maze Editor")
    # for screen in app.screens():
    #     screen_dpi = screen.logicalDotsPerInch()
    #     print(screen_dpi)
    window.setWindowIcon(QIcon('icons/MazeEditSmall.png'))
    window.show()
    sys.exit(app.exec_())
