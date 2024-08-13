from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class ImageDisplayWindow(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Image Display")
        layout = QVBoxLayout()

        # Create a QLabel to display the image
        self.image_label = QLabel()
        self.load_image()
        layout.addWidget(self.image_label)

        # Add a "Save As" button
        save_button = QPushButton("Save As")
        save_button.clicked.connect(self.save_image)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def load_image(self):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            # Scale the image to fit within 800x600 while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.resize(scaled_pixmap.width(), scaled_pixmap.height())
        else:
            self.image_label.setText(f"Failed to load image: {self.image_path}")

    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            pixmap = self.image_label.pixmap()
            pixmap.save(file_name)
