import sys
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QStatusBar, QSplitter
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from .chat_widget import ChatWidget
from .code_editor import CodeEditor
from .workspace_manager import WorkspaceManager
from .settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.setWindowTitle("Open Interpreter")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()

    def init_ui(self):
        self.create_menu_bar()
        self.create_status_bar()

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Chat widget
        self.chat_widget = ChatWidget(self.interpreter)
        splitter.addWidget(self.chat_widget)

        # Right panel: Code editor and Workspace manager
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.code_editor = CodeEditor(self.interpreter, self.chat_widget)
        self.workspace_manager = WorkspaceManager(self.interpreter)

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(self.code_editor)
        right_splitter.addWidget(self.workspace_manager)
        right_splitter.setStretchFactor(0, 2)  # Give more space to code editor
        right_splitter.setStretchFactor(1, 1)

        right_layout.addWidget(right_splitter)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction(QIcon(), "Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        settings_action = QAction(QIcon(), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)

        # View menu
        view_menu = menu_bar.addMenu("View")
        toggle_workspace_action = QAction("Toggle Workspace", self)
        toggle_workspace_action.triggered.connect(self.toggle_workspace)
        view_menu.addAction(toggle_workspace_action)

    def create_status_bar(self):
        status_bar = QStatusBar()
       
