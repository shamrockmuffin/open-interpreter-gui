from interpreter import OpenInterpreter

import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def process_message(self, message):
        try:
            for response in self.interpreter.chat_stream(message):
                yield response
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            yield {"type": "error", "content": f"An error occurred: {str(e)}"}
