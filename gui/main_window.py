import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QMenuBar, QStatusBar, QSplitter, QMessageBox, 
                             QListWidget, QStackedWidget, QPushButton, QComboBox, QTextEdit)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSlot
from gui.chat_widget import ChatWidget
from gui.file_list_widget import FileListWidget
from gui.settings_dialog import SettingsDialog
from gui.file_display_widget import FileDisplayWidget
# from gui.script_display_widget import ScriptDisplayWidget
from gui.config_manager import ConfigManager
from gui.message_handler import MessageHandler
from gui.ui_manager import UIManager

class MainWindow(QMainWindow):
    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.setWindowTitle("Open Interpreter")
        self.setGeometry(100, 100, 1200, 800)

        self.chat_widgets = []
        self.file_list_widget = None
        self.file_display = None
        self.script_display = None
        self.config_manager = ConfigManager()
        self.message_handler = MessageHandler(self.interpreter)

        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()
        self.connect_components()
        self.load_settings()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Left panel: Model selection and chat list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.model_selector = QComboBox()
        self.model_selector.addItems(self.config_manager.load_config()['available_models'])
        self.model_selector.setCurrentText(self.config_manager.load_config()['default_model'])
        self.model_selector.currentTextChanged.connect(self.on_model_changed)
        left_layout.addWidget(self.model_selector)
        
        self.chat_list = QListWidget()
        left_layout.addWidget(self.chat_list)
        
        new_chat_button = QPushButton("New Chat")
        new_chat_button.clicked.connect(self.create_new_chat)
        left_layout.addWidget(new_chat_button)

        # Center panel: Chat widget and code output
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        self.chat_stack = QStackedWidget()
        center_layout.addWidget(self.chat_stack)
        
        self.script_display = QTextEdit()
        self.script_display.setReadOnly(True)
        center_layout.addWidget(self.script_display)

        # Right panel: File list and file display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.file_list_widget = FileListWidget(self.interpreter, self.chat_widgets)
        right_layout.addWidget(self.file_list_widget)
        
        self.file_display = FileDisplayWidget()
        right_layout.addWidget(self.file_display)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(center_panel, 2)
        main_layout.addWidget(right_panel, 1)

        self.setCentralWidget(main_widget)

        # Create UI Manager
        self.ui_manager = UIManager()
        center_layout.addWidget(self.ui_manager)

    def create_new_chat(self):
        new_chat = ChatWidget(self.interpreter, self.message_handler, self.file_list_widget, self.ui_manager)
        self.chat_widgets.append(new_chat)
        self.chat_stack.addWidget(new_chat)
        self.chat_stack.setCurrentWidget(new_chat)
        
        chat_item = f"Chat {len(self.chat_widgets)}"
        self.chat_list.addItem(chat_item)
        self.chat_list.setCurrentRow(self.chat_list.count() - 1)
        
        new_chat.set_file_list_widget(self.file_list_widget)
        new_chat.set_main_window(self)
        new_chat.file_operation_occurred.connect(self.script_display.display_file_operation)
        new_chat.message_sent.connect(self.process_message)

    def on_model_changed(self, model):
        config = self.config_manager.load_config()
        config['default_model'] = model
        self.config_manager.save_config(config)
        self.interpreter.llm.model = model

    def handle_file_upload(self, file_path, file_name):
        current_chat = self.chat_stack.currentWidget()
        if current_chat:
            current_chat.handle_file_upload(file_path, file_name)
    def handle_file_upload(self, file_path, file_name):
        current_chat = self.chat_stack.currentWidget()
        if current_chat:
            current_chat.handle_file_upload(file_path, file_name)
        self.file_list_widget.file_uploaded.connect(self.handle_file_upload)
        self.file_list_widget.file_selected.connect(self.display_file)
        self.chat_list.currentRowChanged.connect(self.switch_chat)

    @pyqtSlot(str)
    def process_message(self, message):
        current_chat = self.chat_stack.currentWidget()
        try:
            for response in self.message_handler.process_message(message):
                current_chat.update_chat(response)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def switch_chat(self, index):
        if 0 <= index < self.chat_stack.count():
            self.chat_stack.setCurrentIndex(index)

    def upload_file(self):
        file_path, file_name = self.file_list_widget.upload_file()
        current_chat = self.chat_stack.currentWidget()
        if current_chat:
            current_chat.handle_file_upload(file_path, file_name)

    def handle_file_operation(self, operation, filename, content):
        self.script_display.setText(f"{operation} - {filename}:\n{content}\n")
        self.file_list_widget.refresh_file_list()
        language = self.detect_language(filename)
        self.update_status_bar({"file_path": filename, "language": language})

    def detect_language(self, filename):
        extension = filename.split('.')[-1].lower()
        language_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'html': 'HTML',
            'css': 'CSS',
            'json': 'JSON',
            'txt': 'Plain Text'
        }
        return language_map.get(extension, 'Unknown')
    def display_file(self, file_path):
        self.file_display.clear()
        file_extension = file_path.split('.')[-1].lower()
        try:
            if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                self.file_display.display_image(file_path)
            elif file_extension in ['mp3', 'wav']:
                self.file_display.display_audio(file_path)
            elif file_extension in ['mp4', 'avi', 'mov']:
                self.file_display.display_video(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.file_display.display_text(content)
        except Exception as e:
            self.file_display.display_error(f"Error displaying file: {str(e)}")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        
        upload_action = QAction(QIcon(), "Upload File", self)
        upload_action.setShortcut("Ctrl+U")
        upload_action.triggered.connect(self.upload_file)
        file_menu.addAction(upload_action)

        file_menu.addSeparator()

        exit_action = QAction(QIcon(), "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        settings_action = QAction(QIcon(), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)

    def closeEvent(self, event):
        if self.chat_stack:
            self.save_chat_history()
        super().closeEvent(event)

    def save_chat_history(self):
        if self.chat_stack:
            current_chat = self.chat_stack.currentWidget()
            chat_history = current_chat.chat_display.toPlainText()
            if not chat_history.strip():
                return

        if not os.path.exists("GUI_chat_history"):
            os.makedirs("GUI_chat_history")

        timestamp = datetime.now().strftime("chat_%Y%m%d_%H%M%S")
        file_path = os.path.join("GUI_chat_history", f"{timestamp}.txt")

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(chat_history)

    def open_settings(self):
        settings_dialog = SettingsDialog(self.interpreter, self.config_manager)
        if settings_dialog.exec():
            self.apply_settings()

    def apply_settings(self):
        config = self.config_manager.load_config()
        self.interpreter.llm.model = config.get('model', 'gpt-4o')
        self.interpreter.llm.context_length = config.get('context_window', 25000)
        self.interpreter.llm.temperature = config.get('temperature', 0.7)
        self.interpreter.api_base = config.get('api_base', 'https://openrouter.ai/api/v1')

    def load_settings(self):
        self.apply_settings()

    def handle_file_operation(self, operation, filename, content):
        self.script_display.display_file_operation(operation, filename, content)
        self.file_list_widget.refresh_file_list()

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def update_status_bar(self, content_info):
        file_path = content_info['file_path'] or "Untitled"
        language = content_info['language']
        self.statusBar().showMessage(f"File: {file_path} | Language: {language}")
