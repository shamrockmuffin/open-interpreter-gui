from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class SettingsDialog(QDialog):
    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        # Example setting: Language model selection
        layout.addWidget(QLabel("Select Language Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(["Model A", "Model B", "Model C"])
        layout.addWidget(self.model_selector)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        selected_model = self.model_selector.currentText()
        self.interpreter.llm.model = selected_model
        self.accept()
