from gui.interpreter_setup import setup_interpreter

def setup_interpreter():
    config_manager = ConfigManager()
    config = config_manager.default_config

    interpreter = OpenInterpreter()
    interpreter.system_message = "You are Open Interpreter, a world-class programmer that can complete any goal by writing and executing code."
    interpreter.auto_run = True
    interpreter.api_base = config.get('api_base', 'https://openrouter.ai/api/v1')
    interpreter.model = config.get('default_model', 'gpt-4o')
    interpreter.api_key = config.get('api_key', '')
    interpreter.site_url = config.get('site_url', '')
    interpreter.site_name = config.get('site_name', '')

    return interpreter
