from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat

class InterpreterThread(QThread):
    output_received = pyqtSignal(dict)

    def __init__(self, interpreter, message):
        super().__init__()
        self.interpreter = interpreter
        self.message = message

    def run(self):
        for response in self.interpreter.chat(self.message, display=False, stream=True):
            self.output_received.emit(response)

class ChatWidget(QWidget):
    message_sent = pyqtSignal(str)

    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.current_message = {"role": "", "content": ""}
        self.code_editor = None  # Will be set later

        layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

        self.message_sent.connect(self.handle_message)

    def set_code_editor(self, code_editor):
        self.code_editor = code_editor

    def send_message(self):
        message = self.input_field.text()
        if message:
            self.input_field.clear()
            self.message_sent.emit(message)

    def handle_message(self, message):
        self.append_message("User", message)
        self.interpreter.messages.append({
            "role": "user",
            "type": "message",
            "content": message
        })
        self.process_message(message)

    def process_message(self, message):
        if message.lower().startswith("analyze this file"):
            if self.code_editor:
                file_info = self.code_editor.get_current_content()
                analysis_message = f"Please analyze this {file_info['language']} file "
                if file_info['file_path']:
                    analysis_message += f"('{file_info['file_path']}')"
                analysis_message += f":\n\n```{file_info['language']}\n{file_info['content']}\n```"
                self.interpreter_thread = InterpreterThread(self.interpreter, analysis_message)
            else:
                self.append_message("System", "No file is currently open in the editor.")
                return
        else:
            self.interpreter_thread = InterpreterThread(self.interpreter, message)
        
        self.interpreter_thread.output_received.connect(self.handle_interpreter_output)
        self.interpreter_thread.start()

    def handle_interpreter_output(self, response):
        if response['type'] == 'message':
            if response.get('start', False):
                self.current_message = {"role": "AI", "content": ""}
            self.current_message["content"] += response.get('content', '')
            if response.get('end', False):
                self.append_message(self.current_message["role"], self.current_message["content"])
                self.current_message = {"role": "", "content": ""}
        elif response['type'] == 'code':
            if response.get('start', False):
                self.current_message = {"role": "AI", "content": "", "language": response.get('language', 'python')}
            self.current_message["content"] += response.get('content', '')
            if response.get('end', False):
                self.append_code(self.current_message["content"], self.current_message["language"])
                self.current_message = {"role": "", "content": ""}
        elif response['type'] == 'console' and response.get('format') == 'output':
            self.append_console_output(response.get('content', ''))

    def append_message(self, sender, content):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        format = QTextCharFormat()
        if sender == "User":
            format.setForeground(QColor("blue"))
        elif sender == "System":
            format.setForeground(QColor("green"))
        else:
            format.setForeground(QColor("red"))
        
        cursor.insertText(f"{sender}: ", format)
        cursor.insertText(f"{content}\n\n")
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

    def display_analysis(self, content_info):
        self.append_message("System", f"Analyzing file: {content_info.get('file_path', 'Unsaved File')}")
        self.process_message(f"Analyze this {content_info['language']} file:\n\n```{content_info['language']}\n{content_info['content']}\n```")