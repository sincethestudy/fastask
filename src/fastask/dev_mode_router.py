from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
import os
import platform
import requests
import json 

from .utils import get_last_n_history, add_to_history

load_dotenv()

def AZURE_client(messages):
    print("\033[91mFASTASK-dev-mode: Using Azure OpenAI\033[0m")
    api_key=os.environ.get("AZURE_OPENAI_API_KEY")
    resource = os.environ.get("AZURE_RESOURCE_GROUP")
    deployment_name=os.environ.get("AZURE_DEPLOYMENT_NAME")

    if not api_key or not resource or not deployment_name:
        raise ValueError("One or more environment variables are not set correctly. Please check AZURE_OPENAI_API_KEY, AZURE_RESOURCE_GROUP, and AZURE_DEPLOYMENT_NAME in your .env file (SEE DOCS).")

    client = AzureOpenAI(
        api_key=api_key,
        api_version="2023-12-01-preview",
        azure_endpoint = "https://{}.openai.azure.com".format(resource),
    )

    completion_stream = client.chat.completions.create(
        messages=messages,
        model=deployment_name,
        stream=False,
        user='fastaskapi'
    )

    return {"response": completion_stream.choices[0].message.content}

def GROQ_client(messages):
    print("\033[91mFASTASK-dev-mode: Using Groq\033[0m")
    api_key=os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("One or more environment variables are not set correctly. Please set GROQ_API_KEY in your .env file (SEE DOCS).")

    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        messages=messages,
        model="llama2-70b-4096",
    )

    return {"response": response.choices[0].message.content}

def OPENAI_client(messages):
    print("\033[91mFASTASK-dev-mode: Using OpenAI\033[0m")
    api_key=os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("One or more environment variables are not set correctly. Please set OPENAI_API_KEY in your .env file (SEE DOCS).")

    client = OpenAI(
        api_key=api_key,
    )

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo-0125",
    )

    return {"response": response.choices[0].message.content}

def TOGETHERAI_client(messages):
    print("\033[91mFASTASK-dev-mode: Using TogetherAI\033[0m")
    api_key=os.environ.get("TOGETHERAI_API_KEY")

    if not api_key:
        raise ValueError("One or more environment variables are not set correctly. Please set TOGETHERAI_API_KEY in your .env file (SEE DOCS).")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.together.xyz/v1",
    )

    response = client.chat.completions.create(
        messages=messages,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    )

    return {"response": response.choices[0].message.content}

# Edit this function
def dev_endpoint(q):
    messages = []

    # System Prompt
    messages.append({
        "role": "system", "content": """You are a command line utility that answers questions quickly and briefly in JSON format.

If there were a few commands you could have given, show them all. Remember that you print to a console, so make it easy to read when possible. The user is on the operating system: """ + platform.system() + """. Bias towards short answers always, each row should fit in one unwrapped line of the terminal, less than 40 characters! Only 3 rows maximum.

Always follow this format:

[
{"command": <command string>:, "desc": <description string>}
]"""
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

    history = get_last_n_history(5)  # Get the last 5 entries

    if history:
        for entry in history:
            messages.extend([
                {"role": "user", "content": entry["Question"]},
                {"role": "assistant", "content": entry["Answer"]}
            ])

    messages.append({
        "role": "user", "content": q
    })

    # response = requests.post(url="https://fastask.fly.dev/itsfast", json={"messages": messages}).json()
    # response = requests.post(url="http://0.0.0.0:8080/itsfast", json={"messages": messages}).json()  # For local dev with a local endpoint SEE dev_mode_router.py for easier deving
    response = GROQ_client(messages)
    # response = AZURE_client(messages)
    # response = OPENAI_client(messages)
    # response = TOGETHERAI_client(messages)

    try:
        striped_response = json.loads(response['response'].replace('```json', '').replace('```', ''))
    except:
        print(response['response'])
        exit()


    for i, item  in enumerate(striped_response):
        print(str(i+1)+". " + "\'" + item['command'] + "\'" + " - " + item['desc'])

    print()
    print()
    add_to_history(q, response['response'])