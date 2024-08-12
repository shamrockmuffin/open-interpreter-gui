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

interpreter = OpenInterpreter()
interpreter.system_message = "You are Open Interpreter, a world-class programmer that can complete any goal by writing and executing code."
interpreter.auto_run = True
interpreter.api_base = "https://openrouter.ai/api/v1"
interpreter.model = "openai/gpt-4-vision-preview"
interpreter.api_key = "YOUR_OPENROUTER_API_KEY_HERE"
message_handler = MessageHandler(interpreter)
file_upload_handler = FileUploadHandler()
ui_manager = UIManager()
chat_widget = ChatWidget(interpreter, message_handler, file_upload_handler, ui_manager)



