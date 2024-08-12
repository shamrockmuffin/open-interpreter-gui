import os
from datetime import datetime
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QStatusBar, QSplitter
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from .chat_widget import ChatWidget
from .code_editor import CodeEditor
from .settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.setWindowTitle("Open Interpreter")
        self.setGeometry(100, 100, 1200, 800)

        self.chat_widget = None
        self.code_editor = None

        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()
        self.connect_components()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Chat widget
        self.chat_widget = ChatWidget(self.interpreter)
        splitter.addWidget(self.chat_widget)

        # Right panel: Code editor
        self.code_editor = CodeEditor(self.interpreter, self.chat_widget)
        splitter.addWidget(self.code_editor)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

    def connect_components(self):
        self.chat_widget.set_code_editor(self.code_editor)
        self.code_editor.analysis_complete.connect(self.chat_widget.display_analysis)
        self.code_editor.content_changed.connect(self.update_status_bar)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        
        open_action = QAction(QIcon(), "Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.code_editor.open_file)
        file_menu.addAction(open_action)

        save_action = QAction(QIcon(), "Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.code_editor.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction(QIcon(), "Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.code_editor.save_file_as)
        file_menu.addAction(save_as_action)

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
        settings_dialog = SettingsDialog(self.interpreter)
        settings_dialog.exec()

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def update_status_bar(self, content_info):
        file_path = content_info['file_path'] or "Untitled"
        language = content_info['language']
        self.statusBar().showMessage(f"File: {file_path} | Language: {language}")
