import tempfile
import os
import json

class History:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.history_file_path = os.path.join(self.temp_dir, 'ask_history.json')
        self.max_history_length = 5

    def add(self, question, answer):
        history_entry = {"Question": question, "Answer": answer}

        if not os.path.exists(self.history_file_path):
            with open(self.history_file_path, 'w') as f:
                json.dump([history_entry], f)
        else:
            try:
                with open(self.history_file_path, 'r') as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                history = []

            history.append(history_entry)

            if len(history) > self.max_history_length:
                history = history[-self.max_history_length:]

            with open(self.history_file_path, 'w') as f:
                json.dump(history, f)

    def get(self, n):
        if not os.path.exists(self.history_file_path):
            return []

        with open(self.history_file_path, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                return []

        return history[-n:]

    def clear_history(self):
        if os.path.exists(self.history_file_path):
            os.remove(self.history_file_path)
        with open(self.history_file_path, 'w') as f:
            pass  # Create the file if it doesn't exist
