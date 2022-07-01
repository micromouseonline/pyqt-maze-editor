# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# Copyright (c) Peter Harrison 2022
# License: MIT
# description: A Maze Editor written using PyQt5
# python version >= 3.8
# ============================================================================ #

from PyQt5 import QtCore, QtGui, QtWidgets


class MazeView(QtWidgets.QGraphicsView):
    # photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    maze_clicked = QtCore.pyqtSignal(QtCore.QPoint, int, int)

    def __init__(self, parent):
        super(MazeView, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self.panning = False
        self._pan_start_x = 0
        self._pan_start_y = 0

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def resizeEvent(self, event):
        bounds = self.sceneRect()
        bounds.adjust(-20, -20, 40, 40)
        self.fitInView(bounds, QtCore.Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        # if self.hasPhoto():
        factor = 1.0
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            if self._zoom > 0:
                factor = 0.8
                self._zoom -= 1
        if self._zoom > 0:
            self.scale(factor, factor)
        else:
            self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

    ### mouse dragging method from https://github.com/jonntd/Rigganator
    ### in the characterview class
    ### see also: https://stackoverflow.com/questions/18551466/qt-proper-method-to-implement-panningdrag
    ### and https://stackoverflow.com/questions/4753681/how-to-pan-images-in-qgraphicsview/5156978#5156978
    def mousePressEvent(self, event):
        """
        @note: somehow the dragMode has to be set to NoDrag before being set
                  to either RubberBandDrag or ScrollHandDrag.
        @param event: the event
        @type event: object
        """
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            event = self.fake_left_mouse_button_event(event)
            self.panning = True
        else:
            if self.panning == False:
                ## otherwise odd messages get passed - WHY?
                pos = self.mapToScene(event.pos()).toPoint()
                self.maze_clicked.emit(pos, event.buttons(), event.modifiers())
        super(MazeView, self).mousePressEvent(event)

    def fake_left_mouse_button_event(self, event):
        """Constructs an event that simulates that the left mouse button has
        been pressed. This event is used to work around the flaw that, the
        ScrollHandDrag  mode only works with a pressed left mouse button.
        This way any mouse button can trigger the scrolling.
        @param event: the event
        @type event: object
        """
        event = QtGui.QMouseEvent(event.type(), event.pos(),
                                  event.globalPos(), QtCore.Qt.MouseButton.LeftButton,
                                  event.buttons(), event.modifiers())
        return event

    # END def fake_left_mouse_button_event

    def mouseReleaseEvent(self, event):
        """
        @param event: the event
        @type event: object
        """
        if self.panning:
            self.panning = False
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            # event = self.fake_left_mouse_button_event(event)
        super(MazeView, self).mouseReleaseEvent(event)
