from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit

class SettingsDialog(QDialog):
    def __init__(self, interpreter, config_manager):
        super().__init__()
        self.interpreter = interpreter
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 350)

        layout = QVBoxLayout()

        # Model selector
        layout.addWidget(QLabel("Select Language Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(["gpt-4-turbo", "gpt-4o", "gpt-4o-mini"])
        layout.addWidget(self.model_selector)

        # Context Window
        layout.addWidget(QLabel("Context Window:"))
        self.context_window = QLineEdit()
        layout.addWidget(self.context_window)

        # Temperature
        layout.addWidget(QLabel("Temperature:"))
        self.temperature = QLineEdit()
        layout.addWidget(self.temperature)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.load_current_settings()

    def load_current_settings(self):
        config = self.config_manager.load_config()
        self.model_selector.setCurrentText(config.get('model', 'gpt-4-turbo'))
        self.context_window.setText(str(config.get('context_window', 25000)))
        self.temperature.setText(str(config.get('temperature', 0.7)))

    def save_settings(self):
        config = {
            'model': self.model_selector.currentText(),
            'context_window': int(self.context_window.text()),
            'temperature': float(self.temperature.text())
        }
        self.config_manager.save_config(config)
        self.accept()
