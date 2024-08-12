import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.interpreter_setup import setup_interpreter
from gui.config_manager import ConfigManager

def main():
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    interpreter = OpenInterpreter()
    main_window = MainWindow(interpreter, config_manager)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
