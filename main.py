import logging
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from interpreter import OpenInterpreter
from gui.message_handler import MessageHandler
from gui.config_manager import ConfigManager
from gui.file_upload_handler import FileUploadHandler
from gui.ui_manager import UIManager
from gui.chat_widget import ChatWidget

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='chat_application.log'
)

def main():
    
    interpreter = setup_interpreter()
    message_handler = MessageHandler(interpreter)
    file_upload_handler = FileUploadHandler()
    ui_manager = UIManager()
    chat_widget = ChatWidget(interpreter, message_handler, file_upload_handler, ui_manager)

    app = QApplication(sys.argv)
    main_window = MainWindow(interpreter)
    main_window.setCentralWidget(chat_widget)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


