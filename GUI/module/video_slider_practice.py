import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSlider, QPushButton, QWidget, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import cv2

class VideoSliderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.playButtonClicked)
        self.video_player = cv2.VideoCapture()
        self.slider_value = 0
        self.timer = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Slider")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        vbox = QVBoxLayout(self.main_widget)
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.play_button)

        self.openVideo()

    def openVideo(self):
        # Open video file
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4);;All Files (*)")
        if filePath:
            self.video_player.open(filePath)
            self.slider.setMaximum(int(self.video_player.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)

    def sliderValueChanged(self, value):
        self.slider_value = value
        self.video_player.set(cv2.CAP_PROP_POS_FRAMES, self.slider_value)
        self.updateFrame()

    def playButtonClicked(self):
        if not self.timer:
            self.timer = self.canvas.new_timer(interval=33)  # 30 FPS (1000ms / 30fps = 33ms per frame)
            self.timer.add_callback(self.updateFrame)
            self.timer.start()

        if self.timer._timer and self.timer._timer.is_alive():  # 추가: self.timer._timer가 None이 아닌지 확인
            self.timer.stop()
            self.play_button.setText("Play")
        else:
            self.timer.start()
            self.play_button.setText("Pause")

    def updateFrame(self):
        ret, frame = self.video_player.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.canvas.figure.clf()  # Clear previous plot
            self.canvas.figure.subplots_adjust(left=0, right=1, bottom=0, top=1)
            self.canvas.figure.gca().imshow(frame_rgb)
            self.canvas.draw()

    def closeEvent(self, event):
        self.video_player.release()
        if self.timer:
            self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoSliderApp()
    window.show()
    sys.exit(app.exec_())
