from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import*

class Screen(QMainWindow):
    def setupUi(self):
        self.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        self.screen = QLabel(self.centralwidget)
        self.screen.setPixmap(QPixmap("GUI\icon\water_texture_04.png"))
        self.screen.setScaledContents(True)
        self.screen.setObjectName("screen")
        
        self.gridLayout.addWidget(self.screen, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
    
    def __init__(self):
        super().__init__() 
        self.setupUi()
        self.show()
        
        self.past_x = None
        self.past_y = None
        
        self.present_x = None
        self.present_y = None
        
    # 마우스 MOVE
    def mouseMoveEvent(self,event):
        self.draw_Line(event.x(),event.y())
        
    # 마우스 RELEASE
    def mouseReleaseEvent(self,event):  
        self.draw_Line(event.x(),event.y())
        self.past_x = None
        self.past_y = None

    def draw_Line(self,x,y):
        
        if self.past_x is None:
            self.past_x = x
            self.past_y = y
        else:
            self.present_x = x
            self.present_y = y

            self.img = QPixmap("GUI\icon\water_texture_04.png")
            painter = QPainter(self.img)
            painter.setPen(QPen(Qt.black, 10, Qt.SolidLine))
            painter.drawLine(self.past_x,self.past_y,self.present_x,self.present_y)
            painter.end
            self.screen.setPixmap(QPixmap(self.img))
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Screen()
    sys.exit(app.exec_())