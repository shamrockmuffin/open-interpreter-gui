from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QScrollBar, QProgressBar, QLabel
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer

class UIManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_progress_bar()

    def setup_ui(self):
        self.api_key_label = QLabel("API Key: Not Set")
        self.layout().addWidget(self.api_key_label)
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

    def setup_progress_bar(self):
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.layout().addWidget(self.progress_bar)

    def append_message(self, sender, content):
        format = QTextCharFormat()
        if sender == "User":
            format.setForeground(QColor("blue"))
        elif sender == "System":
            format.setForeground(QColor("green"))
        else:
            format.setForeground(QColor("red"))
        
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(f"{sender}: {content}\n\n", format)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def append_code(self, code, language):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor("purple"))
        
        cursor.insertText(f"Code ({language}):\n", format)
        cursor.insertText(f"{code}\n\n")
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def append_console_output(self, output):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor("gray"))
        
        cursor.insertText("Console Output:\n", format)
        cursor.insertText(f"{output}\n\n")
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def display_image(self, file_path):
        image = QImage(file_path)
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.chat_display.textCursor().insertImage(scaled_pixmap.toImage())
            self.chat_display.append("")  # Add a new line after the image
        else:
            self.chat_display.append(f"Failed to load image: {file_path}")

    def show_progress(self, show=True):
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setValue(0)
            QTimer.singleShot(100, self.update_progress)

    def update_progress(self):
        if self.progress_bar.isVisible():
            value = self.progress_bar.value() + 1
            if value > 100:
                value = 0
            self.progress_bar.setValue(value)
            QTimer.singleShot(100, self.update_progress)
