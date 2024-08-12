



from PyQt6.QtWidgets import QWidget, QTextCursor, QTextCharFormat
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QColor, QImage, QPixmap
import logging


logger = logging.getLogger(__name__)

class InterpreterThread(QThread):
    output_received = pyqtSignal(dict)

    def __init__(self, message_handler, message):
        super().__init__()
        self.message_handler = message_handler
        self.message = message

    def run(self):
        for response in self.message_handler.process_message(self.message):
            self.output_received.emit(response)

class ChatWidget(QWidget):

    file_operation_occurred = pyqtSignal(str, str, str)

    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter



        self.file_list_widget = None
        self.main_window = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        # Setup UI components here
        pass

    def setup_connections(self):



        self.input_field.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)

    def set_file_list_widget(self, file_list_widget):
        self.file_list_widget = file_list_widget

    def set_main_window(self, main_window):
        self.main_window = main_window

    def send_message(self):

        message = self.input_field.text()
        if message:

            self.input_field.clear()
            self.handle_message(message)

    def handle_message(self, message):

        self.append_message("User", message)
        self.interpreter.messages.append({
            "role": "user",
            "type": "message",
            "content": message
        })
        self.process_message(message)



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

    def handle_file_operation(self, operation, filename, content):
        self.file_operation_occurred.emit(operation, filename, content)


    def process_message(self, message):
        try:



            if self.file_list_widget:
                for file_name, file_path in self.file_list_widget.get_uploaded_files().items():
                    if file_name in message:
                        message = message.replace(file_name, file_path)


            self.interpreter_thread = InterpreterThread(self.interpreter, message)
            self.interpreter_thread.output_received.connect(self.handle_interpreter_output)
            self.interpreter_thread.start()

            logger.info(f"Processing message: {message}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

            self.append_message("System", "An error occurred while processing your message.")





    def handle_file_upload(self, file_path, file_name):
        try:


            message = f"File uploaded: {file_name}"
            self.append_message("System", message)
            self.interpreter.messages.append({
                "role": "user",
                "type": "message",
                "content": f"A file named '{file_name}' has been uploaded. You can refer to it in your responses."
            })
            self.process_message(f"Analyze this file: {file_name}")

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