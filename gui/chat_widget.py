import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QScrollBar
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QImage, QPixmap
from gui.interpreter_thread import InterpreterThread
from gui.image_display_window import ImageDisplayWindow

class InterpreterThread(QThread):
    output_received = pyqtSignal(dict)

    def __init__(self, interpreter, message):
        super().__init__()
        self.interpreter = interpreter
        self.message = message

    def run(self):
        for response in self.interpreter.chat(self.message, display=True, stream=True):
            self.output_received.emit(response)

class ChatWidget(QWidget):
    """
    A signal that is emitted when a message is sent.
    
    This signal is emitted by the `ChatWidget` class when the user sends a message through the chat interface. The signal carries the message text as a string.
    """
    message_sent = pyqtSignal(str)
    file_operation_occurred = pyqtSignal(str, str, str)

    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.current_message = {"role": "", "content": ""}
        self.file_list_widget = None  # Will be set later
        self.uploaded_files = {}
        self.main_window = None  # Will be set later

        layout = QVBoxLayout()

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setVerticalScrollBar(QScrollBar())
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
        self.interpreter.file_tracker.file_operation.connect(self.handle_file_operation)

    def set_file_list_widget(self, file_list_widget):
        self.file_list_widget = file_list_widget

    def set_main_window(self, main_window):
        self.main_window = main_window

    def send_message(self):
        message = self.input_field.text()
        if message:
            self.input_field.clear()
            self.message_sent.emit(message)

    def handle_message(self, message):
        """
        Handles a message sent by the user in the chat interface.
        
        This method is called when the user sends a message through the chat interface. It appends the message to the chat display, adds the message to the interpreter's message history, and then processes the message to generate a response.
        
        Args:
            message (str): The text of the message sent by the user.
        """
        self.append_message("User", message)
        self.interpreter.messages.append({
            "role": "user",
            "type": "message",
            "content": message
        })
        self.process_message(message)

    def process_message(self, message):
        """
        Processes a message sent by the user in the chat interface.
        
        This method checks if the message contains any file names that have been uploaded, and replaces those file names with the corresponding file paths. It then creates a new `InterpreterThread` instance, passing the interpreter and the message as arguments, and starts the thread. The `output_received` signal from the `InterpreterThread` instance is connected to the `handle_interpreter_output` method, which will handle the output from the interpreter.
        
        Args:
            message (str): The text of the message sent by the user.
        """
        print(f"Processing message: {message}")  # Debug print
        # Check if the message contains a file name
        for file_name, file_path in self.uploaded_files.items():
            if file_name in message:
                message = message.replace(file_name, file_path)
        
        print(f"Modified message: {message}")  # Debug print
        self.interpreter_thread = InterpreterThread(self.interpreter, message)
        self.interpreter_thread.output_received.connect(self.handle_interpreter_output)
        self.interpreter_thread.start()
        print("InterpreterThread started")  # Debug print



    def handle_interpreter_output(self, response):
          """
          Handles the output received from the interpreter in the chat interface.
        
          This method is called when the `InterpreterThread` instance emits the `output_received` signal, indicating that the interpreter has generated some output. The method checks the type of the output (message, code, or console output) and appends the appropriate content to the chat display using the corresponding `append_*` method.
        
          If the output is a message, the method accumulates the message content until the end of the message is received, and then appends the full message to the chat display.
        
          If the output is code, the method accumulates the code content until the end of the code block is received, and then appends the full code block to the chat display.
        


















          If the output is console output, the method appends the output directly to the chat display.
          """
          if response['type'] == 'message':
              if response.get('start', False):
                  self.current_message = {"role": "assistant", "content": ""}
              self.current_message["content"] += response.get('content', '')
              if response.get('end', False):
                  self.append_message(self.current_message["role"], self.current_message["content"])
                  self.current_message = {"role": "", "content": ""}
          elif response['type'] == 'code':
              if response.get('start', False):
                  self.current_message = {"role": "assistant", "content": "", "language": response.get('language', 'python')}
              self.current_message["content"] += response.get('content', '')
              if response.get('end', False):
                  self.append_code(self.current_message["content"], self.current_message["language"])
                  self.current_message = {"role": "", "content": ""}
          elif response['type'] == 'console' and response.get('format') == 'output':
              self.append_console_output(response.get('content', ''))

    def append_message(self, sender, content):
        """
        Appends a message to the chat display with the specified sender and content.
        
        The message is formatted with the appropriate color based on the sender:
        - "User" messages are displayed in blue
        - "System" messages are displayed in green
        - All other senders are displayed in red
        
        The message is inserted at the end of the chat display, and the cursor is moved to ensure the message is visible.
        
        Args:
            sender (str): The name of the sender of the message.
            content (str): The content of the message.
        """
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
        """
        Appends code to the chat display with the specified language.
        
        The code is formatted with a purple color and inserted at the end of the chat display. The cursor is then moved to ensure the code is visible.
        
        Args:
            code (str): The code to be appended.
            language (str): The programming language of the code.
        """
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

    def handle_file_upload(self, file_paths, file_names):
        for file_name, file_path in zip(file_names, file_paths):
            self.uploaded_files[file_name] = file_path
        self.append_message("System", f"File uploaded: {file_name}")
        self.interpreter.messages.append({
            "role": "assistant",
            "type": "message",
            "content": f"A file named '{file_name}' has been uploaded. You can refer to it in your responses."
        })
        self.process_message(f"Analyze this file: {file_name}")

    def handle_file_operation(self, operation, filename, content):
        """
        Emits a signal to indicate that a file operation has occurred.
        
        Args:
            operation (str): The type of file operation that occurred (e.g. "upload", "download", "delete").
            filename (str): The name of the file involved in the operation.
            content (bytes): The content of the file, if applicable (e.g. for upload or download operations).
        """
        self.file_operation_occurred.emit(operation, filename, content)

    def display_image(self, file_path):
        """
        Displays an image in a separate window.
        
        Args:
            file_path (str): The file path of the image to be displayed.
        
        This method creates a new ImageDisplayWindow to show the image in a separate window.
        It also adds a message to the chat display indicating that an image has been opened.
        """
        image_window = ImageDisplayWindow(file_path, self)
        image_window.show()
        self.append_message("System", f"Opened image: {file_path}")

    def clear_chat(self):
        """
        Clears the chat display, resets the interpreter's message history, and clears the uploaded files dictionary.
        
        This method is used to reset the state of the chat widget, removing all previous messages, file uploads, and interpreter history. It is typically called when the user wants to start a new conversation or clear the chat display.
        """
        self.chat_display.clear()
        self.interpreter.messages = []
        self.uploaded_files = {}
