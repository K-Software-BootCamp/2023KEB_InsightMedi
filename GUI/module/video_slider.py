import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSlider, QLabel, QPushButton, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer
import cv2

class VideoSliderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.video_frame = QLabel()
        self.slider = QSlider(Qt.Horizontal)
        self.play_button = QPushButton("Play")
        self.video_player = cv2.VideoCapture()
        self.timer = QTimer()
        self.slider_value = 0

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Video Slider")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.addWidget(self.video_frame)
        layout.addWidget(self.slider)
        layout.addWidget(self.play_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.play_button.clicked.connect(self.playButtonClicked)

        self.timer.timeout.connect(self.updateFrame)

        self.openVideo()

    def openVideo(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4);;All Files (*)", options=options)
        if filePath:
            self.video_player.open(filePath)
            self.slider.setMaximum(int(self.video_player.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)

    def sliderValueChanged(self, value):
        self.slider_value = value
        self.video_player.set(cv2.CAP_PROP_POS_FRAMES, self.slider_value)
        self.updateFrame()

    def playButtonClicked(self):
        if not self.timer.isActive():
            self.play_button.setText("Pause")
            self.timer.start(33)  # 30 FPS (1000ms / 30fps = 33ms per frame)
        else:
            self.play_button.setText("Play")
            self.timer.stop()

    def updateFrame(self):
        ret, frame = self.video_player.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.video_frame.size(), Qt.KeepAspectRatio)
            self.video_frame.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        self.video_player.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoSliderApp()
    window.show()
    sys.exit(app.exec_())
