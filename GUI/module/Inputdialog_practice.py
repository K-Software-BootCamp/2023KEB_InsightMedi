import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Input Dialog')

        # 첫 번째 값 입력
        self.label1 = QLabel('Enter value 1:')
        self.line_edit1 = QLineEdit()
        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.label1)
        self.layout1.addWidget(self.line_edit1)

        # 두 번째 값 입력
        self.label2 = QLabel('Enter value 2:')
        self.line_edit2 = QLineEdit()
        self.layout2 = QVBoxLayout()
        self.layout2.addWidget(self.label2)
        self.layout2.addWidget(self.line_edit2)

        # 버튼
        self.button = QPushButton('OK')
        self.button.clicked.connect(self.get_values)

        # 전체 레이아웃
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.layout2)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def get_values(self):
        value1 = self.line_edit1.text()
        value2 = self.line_edit2.text()
        print(f'Value 1: {value1}')
        print(f'Value 2: {value2}')
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = InputDialog()
    dialog.exec_()
    sys.exit(app.exec_())
