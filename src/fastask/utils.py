import tempfile
import os
import yaml
import json

# HISTORY UTILS

temp_dir = tempfile.gettempdir()
history_file_path = os.path.join(temp_dir, 'ask_history.json')

def add_to_history(question, answer):
    history_entry = {"Question": question, "Answer": answer}

    if not os.path.exists(history_file_path):
        with open(history_file_path, 'w') as f:
            json.dump([history_entry], f)
    else:
        try:
            with open(history_file_path, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []

        history.append(history_entry)

        if len(history) > 5:
            history = history[-5:]

        with open(history_file_path, 'w') as f:
            json.dump(history, f)

def get_last_n_history(n):
    # Check if the file exists, if not, return an empty list
    if not os.path.exists(history_file_path):
        return []

    with open(history_file_path, 'r') as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            return []

    # Return the last n entries from the history
    return history[-n:]

def clear_history():
    if os.path.exists(history_file_path):
        os.remove(history_file_path)
    with open(history_file_path, 'w') as f:
        pass  # Create the file if it doesn't exist


# CONFIG UTILS

def ensure_config_exists():
    config_dir = os.path.expanduser('~/.config/fastask')
    config_path = os.path.join(config_dir, 'config.yaml')
    
    default_config = {
        'dev_mode': False,
    }
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    if not os.path.isfile(config_path):
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)

def load_config():
    config_path = os.path.expanduser('~/.config/fastask/config.yaml')
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def save_config(config):
    config_path = os.path.expanduser('~/.config/fastask/config.yaml')
    with open(config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)