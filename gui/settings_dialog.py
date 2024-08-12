from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QCheckBox

class SettingsDialog(QDialog):
    def __init__(self, interpreter, config_manager):
        super().__init__()
        self.interpreter = interpreter
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 450)

        layout = QVBoxLayout()

        # Model selector
        self.model_selector = QComboBox()
        self.model_selector.addItems(self.config_manager.load_config()['available_models'])
        layout.addWidget(QLabel("Model:"))
        layout.addWidget(self.model_selector)

        # Default Model selector
        layout.addWidget(QLabel("Default Language Model:"))
        self.default_model_selector = QComboBox()
        self.default_model_selector.addItems(self.config_manager.load_config()['available_models'])
        layout.addWidget(self.default_model_selector)

        # Context Window
        layout.addWidget(QLabel("Context Window:"))
        self.context_window = QLineEdit()
        layout.addWidget(self.context_window)

        # Temperature
        layout.addWidget(QLabel("Temperature:"))
        self.temperature = QLineEdit()
        layout.addWidget(self.temperature)

        # API Base selector
        layout.addWidget(QLabel("API Base:"))
        self.api_base_selector = QComboBox()
        self.api_base_selector.addItems([
            "https://openrouter.ai/api/v1",
            "https://api.openai.com/v1",
            "https://api.anotherprovider.com/v1"
        ])
        layout.addWidget(self.api_base_selector)
        # API Key
        layout.addWidget(QLabel("API Key:"))
        self.api_key = QLineEdit()
        layout.addWidget(self.api_key)

        # Site URL
        layout.addWidget(QLabel("Site URL:"))
        self.site_url = QLineEdit()
        layout.addWidget(self.site_url)

        # Site Name
        layout.addWidget(QLabel("Site Name:"))
        self.site_name = QLineEdit()
        layout.addWidget(self.site_name)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.load_current_settings()

    def load_current_settings(self):
        config = self.config_manager.load_config()
        self.model_selector.setCurrentText(config.get('model', 'gpt-4o'))
        config = self.config_manager.load_config()
        self.model_selector.setCurrentText(config.get('model', 'gpt-4o'))
        self.api_base_selector.setCurrentText(config.get('api_base', 'https://openrouter.ai/api/v1'))
        self.api_key.setText(config.get('api_key', ''))
        self.site_url.setText(config.get('site_url', ''))
        self.site_name.setText(config.get('site_name', ''))
        self.context_window.setText(str(config.get('context_window', 25000)))
        self.temperature.setText(str(config.get('temperature', 0.7)))

    def save_settings(self):
        config = {
            'model': self.model_selector.currentText(),
            'context_window': int(self.context_window.text()),
            'temperature': float(self.temperature.text()),
            'api_base': self.api_base_selector.currentText(),
            'api_key': self.api_key.text(),
            'site_url': self.site_url.text(),
            'site_name': self.site_name.text()
        }
        self.config_manager.save_config(config)
        self.accept()
