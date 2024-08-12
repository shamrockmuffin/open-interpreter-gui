import logging
import sys
import argparse
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from interpreter import OpenInterpreter
from PyQt6.QtGui import QIcon
from gui.message_handler import MessageHandler
from gui.file_upload_handler import FileUploadHandler
from gui.ui_manager import UIManager
from gui.chat_widget import ChatWidget
from gui.message_handler import MessageHandler
from gui.file_upload_handler import FileUploadHandler
from gui.ui_manager import UIManager
from gui.message_handler import MessageHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='chat_application.log'
)

interpreter = OpenInterpreter()
interpreter.system_message = "You are Open Interpreter, a world-class programmer that can complete any goal by writing and executing code."
interpreter.auto_run = True
interpreter.api_base = "https://openrouter.ai/api/v1"
interpreter.model = "openai/gpt-4o"
interpreter.api_key = " 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"
message_handler = MessageHandler(interpreter)
file_upload_handler = FileUploadHandler()
ui_manager = UIManager()
chat_widget = ChatWidget(interpreter, message_handler, file_upload_handler, ui_manager)



