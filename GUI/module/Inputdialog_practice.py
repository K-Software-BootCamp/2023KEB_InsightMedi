import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Input Dialog')

        self.label1 = QLabel('Enter value 1:')
        self.line_edit1 = QLineEdit()

        self.label2 = QLabel('Enter value 2:')
        self.line_edit2 = QLineEdit()

        self.button_ok = QPushButton('OK')
        self.button_ok.clicked.connect(self.accept)

        self.button_cancel = QPushButton('Cancel')
        self.button_cancel.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.line_edit1)
        layout.addWidget(self.label2)
        layout.addWidget(self.line_edit2)
        layout.addWidget(self.button_ok)
        layout.addWidget(self.button_cancel)

        self.setLayout(layout)

    def accept(self):
        value1 = self.line_edit1.text()
        value2 = self.line_edit2.text()

        print('Value 1:', value1)
        print('Value 2:', value2)

        super().accept()

    def reject(self):
        print('Cancel button clicked')
        super().reject()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = InputDialog()
    if dialog.exec_() == QDialog.Accepted:
        sys.exit(app.exec_())
