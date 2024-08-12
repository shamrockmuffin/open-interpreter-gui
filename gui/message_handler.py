from  interpreter import 


class MessageHandler:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def process_message(self, message):
        for response in self.interpreter.chat(message, display=False, stream=True):
            yield response