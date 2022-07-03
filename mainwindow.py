# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# Copyright (c) Peter Harrison 2022
# License: MIT
# description: A Maze Editor written using PyQt5
# python version >= 3.8
# ============================================================================ #

from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import (QByteArray, QFile, QFileInfo, QSaveFile, QSettings,
                          QTextStream, QDir, Qt)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow,
                             QMessageBox, QTextEdit, QWidget, QAction)

import maze
from mainwindow_ui import Ui_MainWindow
from maze import Maze
from mazeitem import MazeItem
import os


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, path='mazefiles', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_not_repaint = True
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.create_actions()
        self.create_menu()
        self.create_tool_bars()
        self.statusBar().showMessage('ready')
        self.read_settings()

        self.recent_files = []
        self.current_file_name = ""

        self.maze_scene = QtWidgets.QGraphicsScene()
        self.maze_item = MazeItem()
        self.maze_scene.addItem(self.maze_item)
        self.maze_note = self.maze_scene.addText("NOTES")

        font = QtGui.QFont()
        font.setPixelSize(45)
        self.maze_note.setFont(font)
        self.maze_note.setDefaultTextColor(QtGui.QColor(QtCore.Qt.yellow))
        self.maze_note.setPos(0, self.maze_item.width + 20)

        self.ui.maze_view.setScene(self.maze_scene)
        self.ui.maze_view.fitInView(self.maze_scene.sceneRect())
        self.ui.maze_view.update()

        self.ui.le_maze_filter.textChanged.connect(self.filter_filenames)

        self.path_to_maze_files = Path(path)
        types = ['**/*.txt', '**/*.maze']
        filenames = []
        for t in types:
            filenames.extend(self.path_to_maze_files.glob(t))
        self.maze_file_names = sorted(
            filename.relative_to(self.path_to_maze_files)
            for filename in list(filenames)
            if filename.is_file()
        )
        self.filter_filenames('')
        self.ui.lw_maze_list.currentItemChanged.connect(self.list_value_changed)
        self.ui.lw_maze_list.setCurrentRow(0)
        self.set_maze(self.ui.lw_maze_list.currentItem().text())
        self.ui.cb_solve_manhattan.setChecked(True)
        self.ui.maze_view.maze_clicked.connect(self.maze_item.on_maze_click)
        # self.ui.pb_button_a.clicked.connect(self.save_file)
        # self.ui.pb_button_b.clicked.connect(self.new_file)
        self.ui.cb_show_costs.stateChanged.connect(self.enable_costs)
        self.ui.cb_show_directions.stateChanged.connect(self.enable_directions)
        self.ui.cb_show_paths.stateChanged.connect(self.enable_paths)

    def create_actions(self):
        icon = QIcon('./icons/filenew.png')
        self._new_act = QAction(icon, "&New", self)
        self._new_act.setShortcut(QKeySequence.New)
        self._new_act.setStatusTip("Create a new file")
        self._new_act.triggered.connect(self.new_file)

        icon = QIcon('./icons/fileopen.png')
        self._open_act = QAction(icon, "&Open...", self)
        self._open_act.setShortcut(QKeySequence.Open)
        self._open_act.setStatusTip("Open an existing file")
        self._open_act.triggered.connect(self.open)

        icon = QIcon('./icons/filesave.png')
        self._save_act = QAction(icon, "&Save", self)
        self._save_act.setShortcut(QKeySequence.Save)
        self._save_act.setStatusTip("Save the maze to disk")
        self._save_act.triggered.connect(self.save)

        self._save_as_act = QAction("Save &As...", self)
        self._save_as_act.setShortcut(QKeySequence.SaveAs)
        self._save_as_act.setStatusTip("Save with a new name")
        self._save_as_act.triggered.connect(self.save_as)

        icon = QIcon('./icons/exit.png')
        self._exit_act = QAction(icon,"E&xit", self, )
        self._exit_act.setShortcut(QKeySequence.Quit)
        self._exit_act.setStatusTip("Exit the application")
        self._exit_act.triggered.connect(self.close)

        self._about_act = QAction("&About", self)
        self._about_act.setStatusTip("Show the About Box")
        self._about_act.triggered.connect(self.about)

        self._about_files_act = QAction("About Files", self)
        self._about_files_act.setStatusTip("About the File Formats")
        self._about_files_act.triggered.connect(self.about_files)

    def create_menu(self):
        self._file_menu = self.menuBar().addMenu("&File")
        self._file_menu.addAction(self._new_act)
        self._file_menu.addAction(self._open_act)
        self._file_menu.addAction(self._save_act)
        self._file_menu.addAction(self._save_as_act)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._exit_act)

        self.menuBar().addSeparator()

        self._help_menu = self.menuBar().addMenu("&Help")
        self._help_menu.addAction(self._about_act)
        self._help_menu.addAction(self._about_files_act)

    def create_tool_bars(self):
        self._file_tool_bar = self.addToolBar("File")
        self._file_tool_bar.addAction(self._new_act)
        self._file_tool_bar.addAction(self._open_act)
        self._file_tool_bar.addAction(self._save_act)
        self._file_tool_bar.addAction(self._exit_act)

    def enable_costs(self,enable):
        if self.maze_item is None:
            return
        if enable:
            self.maze_item.show_costs()
        else:
            self.maze_item.hide_costs()
        self.maze_item.update()

    def enable_directions(self,enable):
        if self.maze_item is None:
            return
        if enable:
            self.maze_item.show_arrows()
        else:
            self.maze_item.hide_arrows()
        self.maze_item.update()

    def enable_paths(self,enable):
        if self.maze_item is None:
            return
        if enable:
            self.maze_item.show_paths()
        else:
            self.maze_item.hide_paths()
        self.maze_item.update()

    def list_value_changed(self, current_item, prev_item):
        if not current_item:
            return
        fname = current_item.text()
        self.set_maze(fname)

    def set_maze(self, fname):
        self.statusBar().showMessage(fname)
        # TODO make this Path a simple string
        maze_file = Path(fname)
        pathname = QDir.currentPath() / self.path_to_maze_files / maze_file
        with open(pathname, 'r') as maze_file:
            # TODO do some error checking here
            new_maze = Maze.parse_maze_file(maze_file)
            self.maze_item.set_maze(new_maze)
        self.set_current_file(str(pathname))
        self.maze_item.update()

    def filter_filenames(self, filter_text):
        keywords = filter_text.lower().split(' ')
        self.ui.lw_maze_list.clear()
        for fname in self.maze_file_names:
            for key in keywords:
                if key not in str(fname).lower():
                    break
            else:
                self.ui.lw_maze_list.addItem(str(fname))
        self.ui.lw_maze_list.setCurrentRow(0)

    def read_settings(self):
        ''' get path and recent files list '''
        settings = QSettings("micromouseonline.com", "pyqt_maze_editor")
        geometry = settings.value('geometry', QByteArray())
        if geometry.size():
            self.restoreGeometry(geometry)
        else:
            self.resize(1200, 900)
        pass

    def write_settings(self):
        ''' save path and recent files list '''
        settings = QSettings("micromouseonline.com", "pyqt_maze_editor")
        settings.setValue('geometry', self.saveGeometry())
        pass

    def maybe_save(self):
        ''' check for unsaved file and save if desired '''
        if self.maze_item.is_modified:
            act = QMessageBox.warning(self, "Application",
                                      "The document has been modified.\nDo you want to save "
                                      "your changes?",
                                      QMessageBox.Save | QMessageBox.Discard |
                                      QMessageBox.Cancel)
            if act == QMessageBox.Save:
                return self.save()
            elif act == QMessageBox.Cancel:
                return False
        return True

    def new_file(self):
        ''' create new empty maze'''
        new_maze = Maze.parse_maze_lines(maze.empty_classic_maze)
        self.current_file_name = ""
        self.maze_item.set_maze(new_maze)
        self.setWindowTitle(F"PyQt Maze Editor - [{self.current_file_name}]")
        pass

    def open(self):
        ''' open existing file after check for changes to existing file '''
        if self.maybe_save():
            filters = "Text files (*.txt);;Maze files (*.maze);;All files (*.*)"
            default_filter = "Text files (*.txt)"
            file_name, file_filter = QFileDialog.getOpenFileName(self, "open file",
                                                                 QtCore.QDir.currentPath(),
                                                                 filters, default_filter);
            if file_name:
                self.load_file(file_name)
        pass

    def open_recent(self):
        ''' open file from recent list after check for changes to existing file '''
        pass

    def save(self):
        """ save file, checking for new name on first save """
        if self.current_file_name:
            return self.save_file(self.current_file_name)
        return self.save_as()

    def save_as(self):
        filters = "Text files (*.txt);;Maze files (*.maze);;All files (*.*)"
        default_filter = "Text files (*.txt)"
        file_name, file_filter = QFileDialog.getSaveFileName(self, "Save file",
                                                             QtCore.QDir.currentPath(),
                                                             filters, default_filter);
        if file_name:
            return self.save_file(file_name)
        return False

    def load_file(self, file_name):
        """ Read maze file from disk """
        with open(file_name, 'r') as file:
            disk_maze = Maze.parse_maze_file(file)
        self.maze_item.set_maze(disk_maze)
        self.set_current_file(file_name)

    def save_file(self, filename):
        """ Saves the maze data to disk """
        lines = self.maze_item.maze.get_maze_string()
        error = None
        file = QSaveFile(filename)
        if file.open(QFile.WriteOnly | QFile.Text):
            output_stream = QTextStream(file)
            output_stream << lines
            if not file.commit():
                reason = file.errorString()
                error = f"Cannot write file {filename}:\n{reason}."
        else:
            reason = file.errorString()
            error = f"Cannot open file {filename}:\n{reason}."
        if error:
            QMessageBox.warning(self, "Unable to Save File", error)
            return False

        self.set_current_file(filename)
        self.statusBar().showMessage("File Saved",2000)
        return True

    def set_current_file(self,filename):
        """ after save/load update recent files and window title """
        self.current_file_name = filename
        name = QFileInfo(self.current_file_name).fileName()
        self.maze_item.is_modified = False
        self.setWindowTitle(F"PyQt Maze Editor - [{name}]")
        self.setWindowModified(False)

    def about(self):
        QMessageBox.about(self, "About PyQt Maze Editor",
                          "Display, Edit and Print micromouse maze files.\n\n"
                          "Any size maze can be loaded and saved.\n\n"
                          "Maze files are stored as plain text. For more information select About | File Formats")

    def about_files(self):
        QMessageBox.about(self, "Maze File Formats",
                          "Text files represent posts and walls as ASCII characters:\n"
                          "\tPosts: '+' or 'o'\n"
                          "\tWalls: '-' or '=' or '|'\n\n"
                          "Text formats may use one or two consecutive symbols to represent a wall "
                          "in order to make printed layouts easier on the eye. This program uses "
                          "triple characters for horizontal walls")

    def closeEvent(self, event):
        if self.maybe_save():
            self.write_settings()
            event.accept()
        else:
            event.ignore()
        pass
