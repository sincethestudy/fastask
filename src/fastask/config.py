import os
import yaml

class Config:
    def __init__(self):
        self.config_dir = os.path.expanduser('~/.config/fastask')
        self.config_path = os.path.join(self.config_dir, 'config.yaml')
        self.default_config = {
            'llm': 'fastask',
            'enable_leaderboard': False,
            'user': ''
        }
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.isfile(self.config_path):
            with open(self.config_path, 'w') as file:
                yaml.dump(self.default_config, file, default_flow_style=False)

    def load(self):
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

    def save(self, config):
        with open(self.config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

    
