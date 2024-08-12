import sys
import argparse
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from interpreter import OpenInterpreter

def main():
    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser(description="Open Interpreter GUI")
    parser.add_argument("--model", help="Specify the language model to use")
    parser.add_argument("--safe-mode", action="store_true", help="Enable safe mode")
    args = parser.parse_args()

    try:
        interpreter = OpenInterpreter()
        if args.model:
            interpreter.llm.model = args.model
        if args.safe_mode:
            interpreter.safe_mode = "auto"

        window = MainWindow(interpreter)
        window.show()
        sys.exit(app.exec())
    except ImportError as e:
        print(f"Error: {e}")
        print("Please make sure all required dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()