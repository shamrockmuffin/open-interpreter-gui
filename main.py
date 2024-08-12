import logging
import sys
import argparse
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from interpreter import OpenInterpreter
from PyQt6.QtGui import QIcon

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='chat_application.log'
)

interpreter = Interpreter()
message_handler = MessageHandler(interpreter)
file_upload_handler = FileUploadHandler()
ui_manager = UIManager()
chat_widget = ChatWidget(interpreter, message_handler, file_upload_handler, ui_manager)



