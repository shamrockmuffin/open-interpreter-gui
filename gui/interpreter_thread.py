"""
Defines an `InterpreterThread` class that runs an interpreter in a separate thread and emits signals when processing starts, finishes, and when output is received.

The `InterpreterThread` class is responsible for running an interpreter in a separate thread and emitting signals to notify the main thread of the interpreter's progress and output. It takes an `interpreter` object and a `message` as input, and runs the interpreter's `chat` method in the separate thread, emitting the `output_received` signal for each response received from the interpreter, the `processing_started` signal when processing begins, and the `processing_finished` signal when processing completes.

The `stop` method can be called to set the `is_running` flag to `False`, which will cause the thread to exit the next time it checks the flag.
"""
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
            print(f"InterpreterThread: Starting chat with message: {self.message}")  # Debug print
            for response in self.interpreter.chat(self.message, display=True, stream=True):
                print(f"InterpreterThread: Received response: {response}")  # Debug print
                self.output_received.emit(response)
        except Exception as e:
            print(f"InterpreterThread: Error occurred: {str(e)}")  # Debug print
        finally:
            print("InterpreterThread: Processing finished")  # Debug print
            self.processing_finished.emit()

    def stop(self):
        self.is_running = False
