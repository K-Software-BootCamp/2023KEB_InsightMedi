import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Windowing')
        self.ok = False

        self.label1 = QLabel('Enter the WL:')
        self.line_edit1 = QLineEdit()

        self.label2 = QLabel('Enter the WW:')
        self.line_edit2 = QLineEdit()

        self.button_ok = QPushButton('OK')
        self.button_ok.clicked.connect(self.accept)

        self.button_cancel = QPushButton('Cancel')
        self.button_cancel.clicked.connect(self.reject)

        # 버튼을 수평으로 정렬하는 수평 레이아웃
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_ok)
        button_layout.addWidget(self.button_cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.line_edit1)
        layout.addWidget(self.label2)
        layout.addWidget(self.line_edit2)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def accept(self):
        value1 = self.line_edit1.text()
        value2 = self.line_edit2.text()

        #print('WL: ', value1)
        #print('WW: ', value2)

        self.ok = True
        super().accept()
    
    def reject(self):
        #print('Cancel button clicked')

        self.ok = False
        super().reject()
    
    def getText(self):
        value1 = self.line_edit1.text()
        value2 = self.line_edit2.text()

        return value1, value2, self.ok


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = InputDialog()
    if dialog.exec_() == QDialog.Accepted:
        sys.exit(app.exec_())
