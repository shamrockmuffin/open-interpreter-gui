



from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QSplitter
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QImage, QPixmap, QTextCursor, QTextCharFormat
import logging
from gui.constants import Colors, MessageTypes, Roles
from gui.interpreter_thread import InterpreterThread

logger = logging.getLogger(__name__)

class ChatWidget(QWidget):
    file_operation_occurred = pyqtSignal(str, str, str)
    message_processed = pyqtSignal(dict)
    message_sent = pyqtSignal(str)

    def __init__(self, interpreter, message_handler, file_upload_handler, ui_manager):
        super().__init__()
        self.interpreter = interpreter
        self.message_handler = message_handler
        self.file_upload_handler = file_upload_handler
        self.ui_manager = ui_manager
        self.file_list_widget = None
        self.main_window = None
        self.setup_ui()
        self.setup_connections()
        self.interpreter_thread = None

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        input_layout.addWidget(self.send_button)

        self.upload_button = QPushButton("Upload File")
        input_layout.addWidget(self.upload_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

    def append_message(self, sender, content):
        self.chat_display.append(f"<b>{sender}:</b> {content}<br>")

    def update_chat(self, response):
        if isinstance(response, dict) and 'content' in response:
            self.append_message("AI", response['content'])
        elif isinstance(response, str):
            self.append_message("AI", response)

    def setup_connections(self):
        self.input_field.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)
        self.upload_button.clicked.connect(self.upload_file)

    def set_file_list_widget(self, file_list_widget):
        self.file_list_widget = file_list_widget

    def set_main_window(self, main_window):
        self.main_window = main_window

    def send_message(self):
        message = self.input_field.text()
        if message:
            self.input_field.clear()
            self.append_message("User", message)
            self.process_message(message)

    def update_chat(self, response):
        self.handle_interpreter_output(response)



    def handle_interpreter_output(self, response):
        if 'type' in response:
            if response['type'] == MessageTypes.MESSAGE:
                content = self.format_content_as_sentences(response.get('content', ''))
                self.append_message(response.get('role', 'System'), content)
            elif response['type'] == MessageTypes.CODE:
                self.append_code(response.get('content', ''), response.get('language', 'python'))
            elif response['type'] == MessageTypes.CONSOLE:
                content = self.format_content_as_sentences(response.get('content', ''))
                self.append_console_output(content)
            else:
                logger.warning(f"Unexpected response type: {response['type']}")
        else:
            logger.warning(f"Missing 'type' in response: {response}")
        
        if 'start' in response or 'end' in response:
            logger.info(f"Received {'start' if 'start' in response else 'end'} flag for {response.get('role', 'unknown')} {response.get('type', 'unknown')}")
        
        self.message_processed.emit(response)

    def format_content_as_sentences(self, content):
        sentences = content.split('. ')
        return '. '.join(sentence.strip() for sentence in sentences if sentence.strip())


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
        cursor.insertText(f"{sender}:\n", format)
        
        for sentence in content.split('\n'):
            if sentence.strip():
                cursor.insertText(f"  {sentence.strip()}\n", format)
        
        cursor.insertText("\n")
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
        for line in output.split('\n'):
            if line.strip():
                cursor.insertText(f"  {line.strip()}\n", format)
        cursor.insertText("\n")
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def handle_file_operation(self, operation, filename, content):
        self.file_operation_occurred.emit(operation, filename, content)


    def process_message(self, message):
        try:
            if self.file_list_widget:
                for file_name, file_path in self.file_list_widget.get_uploaded_files().items():
                    if file_name in message:
                        message = message.replace(file_name, file_path)

            if message.startswith("create_file:"):
                _, file_path, content = message.split(":", 2)
                result = self.interpreter.create_file(file_path.strip(), content.strip())
                self.append_message("System", result)
            elif message.startswith("modify_file:"):
                _, file_path, content = message.split(":", 2)
                result = self.interpreter.modify_file(file_path.strip(), content.strip())
                self.append_message("System", result)
            elif message.startswith("delete_file:"):
                _, file_path = message.split(":", 1)
                result = self.interpreter.delete_file(file_path.strip())
                self.append_message("System", result)
            elif message.startswith("read_file:"):
                _, file_path = message.split(":", 1)
                content = self.interpreter.read_file(file_path.strip())
                self.append_message("System", f"Content of {file_path.strip()}:\n{content}")
            else:
                self.interpreter_thread = InterpreterThread(self.interpreter, message)
                self.interpreter_thread.output_received.connect(self.handle_interpreter_output)
                self.interpreter_thread.processing_started.connect(self.on_processing_started)
                self.interpreter_thread.processing_finished.connect(self.on_processing_finished)
                self.interpreter_thread.start()

            logger.info(f"Processing message: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.append_message("System", "An error occurred while processing your message.")

    def on_processing_started(self):
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        self.append_message("System", "Processing your request...")

    def on_processing_finished(self):
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.append_message("System", "Processing completed.")





    def upload_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Upload File")
        if file_path:
            file_name = os.path.basename(file_path)
            try:
                message = f"File uploaded: {file_name}"
                self.append_message("System", message)
                self.interpreter.messages.append({
                    "role": "user",
                    "type": "message",
                    "content": f"A file named '{file_name}' has been uploaded. You can refer to it in your responses."
                })
                self.process_message(f"Analyze this file: {file_path}")

                logger.info(f"File uploaded: {file_name}")
            except Exception as e:
                logger.error(f"Error handling file upload: {str(e)}")
                self.append_message("System", "An error occurred while uploading the file.")

    def clear_chat(self):

        self.chat_display.clear()
        self.interpreter.messages = []

        if self.file_list_widget:
            self.file_list_widget.clear_list()

    def display_image(self, file_path):
        image = QImage(file_path)
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.chat_display.textCursor().insertImage(scaled_pixmap.toImage())
            self.chat_display.append("")  # Add a new line after the image
        else:






            self.append_message("System", f"Failed to load image: {file_path}")
