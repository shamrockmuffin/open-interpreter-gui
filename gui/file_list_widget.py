import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog
from PyQt6.QtCore import pyqtSignal, Qt

class FileListWidget(QWidget):
    file_uploaded = pyqtSignal(str, str)  # Emit both file path and file name
    file_selected = pyqtSignal(str)  # Emit file path when selected

    def __init__(self, interpreter, chat_widget):
        super().__init__()
        self.interpreter = interpreter
        self.chat_widget = chat_widget
        
        layout = QVBoxLayout()

        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        layout.addWidget(self.file_list)

        # Upload button
        self.upload_button = QPushButton("Upload Files")
        self.upload_button.clicked.connect(self.upload_files)
        layout.addWidget(self.upload_button)

        self.setLayout(layout)

    def upload_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Upload Files")
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            self.add_file_to_list(file_path)
            self.file_uploaded.emit(file_path, file_name)

    def add_file_to_list(self, file_path):
        file_name = os.path.basename(file_path)
        item = QListWidgetItem(file_name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.file_list.addItem(item)

    def on_file_selected(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.file_selected.emit(file_path)

    def get_current_content(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return {'content': '', 'file_path': None}
        
        file_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        return {'content': file_path, 'file_path': file_path}

    def clear_list(self):
        self.file_list.clear()
