import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_config = {
            'available_models': ['gpt-4o', 'gpt-3.5-turbo', 'gemini-1.5-flash', 'palm-2'],
            'default_model': 'gpt-4o',
            'context_window': 25000,
            'temperature': 0.7,
            'api_base': 'https://openrouter.ai/api/v1'
        }

    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                return {**self.default_config, **user_config}
        return self.default_config
