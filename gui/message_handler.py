from interpreter import OpenInterpreter

class MessageHandler:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def process_message(self, message):
        try:
            for response in self.interpreter.chat(message, display=False, stream=True):
                yield response
        except Exception as e:
            yield {"type": "error", "content": str(e)}
