import os
from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QStatusBar, QSplitter, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSlot
from gui.chat_widget import ChatWidget
from gui.file_list_widget import FileListWidget
from gui.settings_dialog import SettingsDialog
from gui.file_display_widget import FileDisplayWidget
from gui.script_display_widget import ScriptDisplayWidget
from gui.config_manager import ConfigManager
from gui.message_handler import MessageHandler

class MainWindow(QMainWindow):
    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.setWindowTitle("Open Interpreter")
        self.setGeometry(100, 100, 1200, 800)

        self.chat_widget = None
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

        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Chat widget
        self.chat_widget = ChatWidget(self.interpreter)
        splitter.addWidget(self.chat_widget)

        # Right panel: File list, File display, and Script display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        top_right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.file_list_widget = FileListWidget(self.interpreter, self.chat_widget)
        self.file_display = FileDisplayWidget()
        top_right_splitter.addWidget(self.file_list_widget)
        top_right_splitter.addWidget(self.file_display)
        
        self.script_display = ScriptDisplayWidget()
        
        right_layout.addWidget(top_right_splitter, 2)
        right_layout.addWidget(self.script_display, 1)
        
        right_panel.setLayout(right_layout)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)
    def connect_components(self):
        self.chat_widget.set_file_list_widget(self.file_list_widget)
        self.chat_widget.set_main_window(self)
        self.file_list_widget.file_uploaded.connect(self.chat_widget.handle_file_upload)
        self.file_list_widget.file_selected.connect(self.display_file)
        self.chat_widget.file_operation_occurred.connect(self.script_display.display_file_operation)
        self.interpreter.file_operation.connect(self.handle_file_operation)
        self.chat_widget.message_sent.connect(self.process_message)

    @pyqtSlot(str)
    def process_message(self, message):
        try:
            for response in self.message_handler.process_message(message):
                self.chat_widget.update_chat(response)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def handle_file_operation(self, operation, filename, content):
        self.script_display.display_file_operation(operation, filename, content)
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
        upload_action.triggered.connect(self.file_list_widget.upload_file)
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
        self.save_chat_history()
        event.accept()

    def save_chat_history(self):
        chat_history = self.chat_widget.chat_display.toPlainText()
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
        self.interpreter.llm.model = config.get('model', 'gpt-4-turbo')
        self.interpreter.llm.context_length = config.get('context_window', 25000)
        self.interpreter.llm.temperature = config.get('temperature', 0.7)

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
