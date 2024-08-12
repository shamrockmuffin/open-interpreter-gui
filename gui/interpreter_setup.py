from gui.config_manager import ConfigManager
from core.core import OpenInterpreter

def setup_interpreter():
    config_manager = ConfigManager()
    config = config_manager.default_config

    interpreter = OpenInterpreter()
    interpreter.system_message = "You are Open Interpreter, a world-class programmer that can complete any goal by writing and executing code."
    interpreter.auto_run = True
    interpreter.api_base = config.get('api_base', 'https://api.openai.com/v1/chat/completions')
    interpreter.model = config.get('default_model', 'gpt-4o')
    interpreter.api_key = config.get('api_key', '')


    return interpreter
