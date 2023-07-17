import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from functools import partial
from GUI.data.dcm_data import DcmData

class LabelList(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.buttons = {}
        self.open_label([0, 1])
        self.setWindowTitle('Label List')
        self.show()

    
    def open_label(self, frames):
        for frame in frames:
            # label = QLabel(label_text)
            button = QPushButton(f"{frame} frame", self)
            self.buttons[button] = frame
            button.clicked.connect(partial(self.btn_clicked, button))
            # self.layout.addWidget(label)
            self.layout.addWidget(button)
        self.update()

    def btn_clicked(self, button):
        print(f"{self.buttons[button]}")
        print(f"btn {button} is clicked")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = LabelList()
    sys.exit(app.exec_())
