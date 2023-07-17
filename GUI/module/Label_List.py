import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class LabelList(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.labels = ["label1", "label2"]
        self.open_label()

        self.setLayout(self.layout)
        self.setWindowTitle('Label List')
        self.show()

    def open_label(self):
        for label_text in self.labels:
            # label = QLabel(label_text)
            button = QPushButton(label_text, self)
            # self.layout.addWidget(label)
            self.layout.addWidget(button)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = LabelList()
    sys.exit(app.exec_())
