from PyQt6.QtCore import QThread, pyqtSignal
import time

class InterpreterThread(QThread):
    output_received = pyqtSignal(dict)
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal()

    def __init__(self, interpreter, message):
        super().__init__()
        self.interpreter = interpreter
        self.message = message
        self.is_running = True

    def run(self):
        self.processing_started.emit()
        try:
            for response in self.interpreter.chat(self.message, display=False, stream=True):
                if not self.is_running:
                    break
                self.output_received.emit(response)
                time.sleep(0.01)  # Small delay to prevent GUI freezing
        finally:
            self.processing_finished.emit()

    def stop(self):
        self.is_running = False
