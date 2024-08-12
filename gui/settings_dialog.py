from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class SettingsDialog(QDialog):
    def __init__(self, interpreter):
        super().__init__()
        self.interpreter = interpreter
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 400, 350)  # Adjust size for additional fields

        layout = QVBoxLayout()

        # Model selector
        layout.addWidget(QLabel("Select Language Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(["gpt-4-turbo", "gpt-4o", "gpt-4o-mini"])  # Update model list from config
        layout.addWidget(self.model_selector)
        #Update Context Window for Selected Model
        layout.addWidget(QLabel("Context Window:"))
        self.context_window = QComboBox()
        self.context_window.addItems(["1000","25000","50000","100000"])
        layout.addWidget(self.context_window)
        #Update Temperature for Selected Model
        layout.addWidget(QLabel("Temperature:"))
        self.temperature = QComboBox()
        self.temperature.addItems(["0.1","0.4","0.7"])
        layout.addWidget(self.temperature)
       



        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_settings(self):
        selected_model = self.model_selector.currentText()
        context_window = self.context_window.currentText()
        temperature = self.temperature.currentText()

        # Update settings in interpreter
        self.interpreter.llm.model = selected_model
        self.interpreter.llm.context_length = int(context_window)
        self.interpreter.llm.temperature = float(temperature)

        self.accept()