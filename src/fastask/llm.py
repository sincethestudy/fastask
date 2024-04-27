from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
import os
import platform
import requests
import json
import re

from .history import History
from .config import Config

load_dotenv()

config_manager = Config()
config = config_manager.load()

class LLM:
    def __init__(self, name):
        self.name = name

    def using(self):
        print(f"\033[91mFASTASK: Using {self.name}\033[0m")

class FastAskClient(LLM):
    def __init__(self):
        super().__init__("FastAsk")

    def create_client(self, messages):
        if config['enable_leaderboard']:
            response = requests.post(url="https://fastask.fly.dev/itsfast", json={"messages": messages, "user": config['user'], "log": True}).json()
            return response
        else:
            response = requests.post(url="https://fastask.fly.dev/itsfast", json={"messages": messages}).json()
            return response

class FastAskLocalClient(LLM):
    def __init__(self):
        super().__init__("FastAsk Local")

    def create_client(self, messages):
        self.using()
        
        if config['enable_leaderboard']==True:
            response = requests.post(url="http://0.0.0.0:8080/itsfast", json={"messages": messages, "user": config['user'], "log": True}).json()
            return response
        else:
            response = requests.post(url="http://0.0.0.0:8080/itsfast", json={"messages": messages}).json()
        return response

class AzureClient(LLM):
    def __init__(self):
        super().__init__("Azure OpenAI")
        self.api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.resource = os.environ.get("AZURE_RESOURCE_GROUP")
        self.deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME")

    def create_client(self, messages):
        self.using()
        client = AzureOpenAI(
            api_key=self.api_key,
            api_version="2023-12-01-preview",
            azure_endpoint=f"https://{self.resource}.openai.azure.com"
        )
        completion_stream = client.chat.completions.create(
            messages=messages,
            model=self.deployment_name,
            stream=False,
            user='fastaskapi'
        )
        return {"response": completion_stream.choices[0].message.content}

class GroqClient(LLM):
    def __init__(self):
        super().__init__("Groq")
        self.api_key = os.environ.get("GROQ_API_KEY")

    def create_client(self, messages):
        self.using()
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        response = client.chat.completions.create(
            messages=messages,
            model="llama2-70b-4096"
        )
        return {"response": response.choices[0].message.content}

class OpenAIClient(LLM):
    def __init__(self):
        super().__init__("OpenAI")
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def create_client(self, messages):
        self.using()
        client = OpenAI(
            api_key=self.api_key
        )
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo-0125"
        )
        return {"response": response.choices[0].message.content}

class TogetherAIClient(LLM):
    def __init__(self):
        super().__init__("TogetherAI")
        self.api_key = os.environ.get("TOGETHERAI_API_KEY")

    def create_client(self, messages):
        self.using()
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.together.xyz/v1"
        )
        response = client.chat.completions.create(
            messages=messages,
            model="mistralai/Mixtral-8x7B-Instruct-v0.1"
        )
        return {"response": response.choices[0].message.content}
    
def parse_response(response):
    pattern = r'\[\s*\{\s*"command"\s*:\s*"(.*?)"\s*,\s*"desc"\s*:\s*"(.*?)"\s*\}\s*(?:,\s*\{\s*"command"\s*:\s*"(.*?)"\s*,\s*"desc"\s*:\s*"(.*?)"\s*\}\s*)*\]'
    matches = re.findall(pattern, response, re.DOTALL)

    commands = []
    for match in matches:
        for i in range(0, len(match), 2):
            if match[i] and match[i+1]:
                commands.append({"command": match[i], "desc": match[i+1]})

    return commands


def askLLM(q, client_type):
    messages = []
    history_manager = History()

    # System Prompt
    messages.append({
        "role": "system", "content": """Lets play a game of knowledge and formatting. We are playing a command line knowledge game. You are a command line utility that answers questions quickly and briefly in JSON format. If there were a few commands you could have given, show them all. Remember that you print to a console, so make it easy to read when possible. The user is on the operating system: """ + platform.system() + """. Bias towards short answers always, each row should fit in one unwrapped line of the terminal, less than 40 characters! Only 3 rows maximum. Always follow this format:\n[\n{"command": <command string>:, "desc": <description string>},\n]\nIts extremely important to follow this response structure."""
    })

    # Fake Examples
    messages.extend([
        {"role": "user", "content": "how do i convert image size in ffmpeg"},
        {"role": "assistant", "content":"""[
{"command": "ffmpeg -i input.jpg -filter:v scale=h=1024 output.jpg", "desc": "Resizes the image to a height of 1024 pixels."},
{"command": "ffmpeg -i input.jpg -filter:v scale=w:h=1:1 output.jpg", "desc": "Resizes image to width and height that are equal"},
{"command": "ffmpeg -i input.jpg -filter:v scale=force_original output.jpg", "desc": "Preserving original aspect ratio."}
]"""},

        {"role": "user", "content": "list items in dir by date"},
        {"role": "assistant", "content":"""[
{"command": "ls -lt", "desc": "List items sorted by date (newest first)."},
{"command": "ls -ltr", "desc": "Added 'r' sorts by oldest first."}
]"""},

        {"role": "user", "content": "how do i make a new docker to run a fresh ubuntu to test on"},
        {"role": "assistant", "content":"""[
{"command": "docker run -it ubuntu", "desc": "Runs a new Docker container with Ubuntu."},
{"command": "docker run -it ubuntu bash", "desc": "also opens a bash shell."}
]"""},

        {"role": "user", "content": "find text in files in linux"},
        {"role": "assistant", "content":"""[
{"command": "grep 'text' *", "desc": "Search in current directory."},
{"command": "grep -r 'text' .", "desc": "Recursive search."},
{"command": "find / -type f -exec grep -l 'text' {} +", "desc": "Find in all files."}
]"""},

        {"role": "user", "content": "how to change file permissions in linux"},
        {"role": "assistant", "content":"""[
{"command": "chmod 755 filename", "desc": "rwx for owner, rx for others."},
{"command": "chmod +x filename", "desc": "Make file executable for all."},
{"command": "chmod u+w,g-w,o=r filename", "desc": "Set specific permissions."}
]"""}
    ])

    # Retrieve and append history
    history = history_manager.get(5)  # Get the last 5 entries
    if history:
        for entry in history:
            messages.extend([
                {"role": "user", "content": entry["Question"]},
                {"role": "assistant", "content": entry["Answer"]}
            ])

    # Add user query
    messages.append({
        "role": "user", "content": q + "\n\n Please respond with the correct structure for grading."
    })

    client = {
        "fastask": FastAskClient(),
        "fastask-local": FastAskLocalClient(),
        "azure": AzureClient(),
        "groq": GroqClient(),
        "openai": OpenAIClient(),
        "togetherai": TogetherAIClient()
    }.get(client_type)

    if not client:
        raise ValueError("Invalid client type specified.")

    response = client.create_client(messages)

    try:
        commands = parse_response(response["response"])
        if not commands:
            raise ValueError("No commands found. Please ensure your query is correct.")
        for i, item in enumerate(commands):
            print(f"{i+1}. '{item['command']}' - {item['desc']}")
        history_manager.add(q, response['response'])
    except:
        print(response['response'])
        print("\033[91mhmm... something went wrong...try again maybe?\033[0m")
        exit()

    print()
    print()
