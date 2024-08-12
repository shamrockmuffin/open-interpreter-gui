from PyQt6.QtCore import QThread, pyqtSignal

class InterpreterThread(QThread):
    output_received = pyqtSignal(dict)

    def __init__(self, interpreter, message):
        super().__init__()
        self.interpreter = interpreter
        self.message = message

    def run(self):
        for response in self.interpreter.chat(self.message, display=False, stream=True):
            self.output_received.emit(response)
