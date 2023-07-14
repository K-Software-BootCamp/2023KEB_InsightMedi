import matplotlib.pyplot as plt
import numpy as np
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5.QtGui import QPainter, QCursor, QPen, QColor, QBrush
from PyQt5.QtCore import Qt

class Draw:
    def __init__(self, main, mode):
        self.main = main
        self.x = None
        self.y = None
        self.end_x = None
        self.end_y = None
        self.mode = mode
    
    def mousePressEvent(self, event):
        if self.mode == "rectangle":
            self.x = event.pos().x()
            self.y = event.pos().y()
    
    def mouseReleaseEvent(self, event):
        if self.mode == "rectangle":
            self.end_x = event.pos().x()
            self.end_y = event.pos().y()
            self.main.update()
    
    def toggle(self, mode):
        if self.mode == "rectangle":
            self.main.setCursor(Qt.CrossCursor)
        else:
            self.main.setCursor(Qt.ArrowCursor)
    
    def paintEvent(self, event):
        if self.mode == "rectangle":
            painter = QPainter(self.main)
            pen = QPen(QColor(0, 0, 0))
            brush = QBrush(QColor(255, 0, 0, 100))
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(self.x, self.y, self.end_x - self.x, self.end_y - self.y)
            