import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt

class FileListWidget(QWidget):
    file_uploaded = pyqtSignal(str, str)  # Emit both file path and file name
    file_selected = pyqtSignal(str)  # Emit file path when selected

    def __init__(self, interpreter, chat_widgets):
        super().__init__()
        self.interpreter = interpreter
        self.chat_widgets = chat_widgets
        
        layout = QVBoxLayout()

        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        layout.addWidget(self.file_list)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Upload button
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        button_layout.addWidget(self.upload_button)

        # Download button
        self.download_button = QPushButton("Download File")
        self.download_button.clicked.connect(self.download_file)
        button_layout.addWidget(self.download_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload File")
        if file_path:
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

    def refresh_file_list(self):
        self.clear_list()
        for file_path in self.interpreter.workspace_manager.get_files():
            self.add_file_to_list(file_path)

    def get_uploaded_files(self):
        uploaded_files = {}
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            file_name = item.text()
            file_path = item.data(Qt.ItemDataRole.UserRole)
            uploaded_files[file_name] = file_path
        return uploaded_files
