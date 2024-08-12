from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QScrollBar
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QImage, QPixmap

class UIManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setVerticalScrollBar(QScrollBar())
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def append_message(self, sender, content):
        self.chat_display.append(f"{sender}: {content}")

    def append_code(self, code, language):
        self.chat_display.append(f"```{language}\n{code}\n```")

    def append_console_output(self, output):
        self.chat_display.append(f"Console output: {output}")

    def display_image(self, file_path):
        image = QImage(file_path)
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            self.chat_display.textCursor().insertImage(pixmap.toImage())
        else:
            self.chat_display.append(f"Failed to load image: {file_path}")
