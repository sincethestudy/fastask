import sys
import os
import argparse
import platform
import json
import requests

from .utils import ensure_config_exists, load_config, save_config, get_last_n_history, clear_history, add_to_history
from .dev_mode_router import dev_endpoint

def check_and_run_command(history, question):
    if question.lower() == 'history':
        history = get_last_n_history(1)
        if history:
            prev_answer = json.loads(history[-1]["Answer"])
            for i, item  in enumerate(prev_answer):
                print(str(i+1)+". " + "\'" + item['command'] + "\'" + " - " + item['desc'])
        else:
            print("No history available.")
        print()
        exit()

    # Check if the question can be converted to an integer
    try:
        index = int(question)
        history = get_last_n_history(5)

        if history:
            answer = history[-1]["Answer"]
            answer_json = json.loads(answer)
            if index <= len(answer_json):
                command = answer_json[index-1]["command"]
                print("\033[94mrunning `" + command + "`...\033[0m")
                os.system(command)
            else:
                print("No command at this index in the answer.")
        else:
            print("No history available.")
        exit()
    except ValueError:
        pass  # The question is not an integer, so we treat it as a question

def call_the_fastest_endpoint_ever(q):

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

    response = requests.post(url="https://fastask.fly.dev/itsfast", json={"messages": messages}).json()
    
    try:
        striped_response = json.loads(response['response'].replace('```json', '').replace('```', ''))
    except:
        print(response['response'])
        print("\033[91mhmm... something went wrong...try again maybe?\033[0m")
        exit()

    try:
        for i, item  in enumerate(striped_response):
            print(str(i+1)+". " + "\'" + item['command'] + "\'" + " - " + item['desc'])
    except:
        print(response['response'])
        print("\033[91mhmm... something went wrong...try again maybe?\033[0m")
        exit()

    print()
    print()
    add_to_history(q, response['response'])

def call_dev_mode_router(q):
    print("\033[91mFASTASK-dev-mode: Using Dev Mode Router\033[0m")
    dev_endpoint(q)
    

def main():
    ensure_config_exists()
    config = load_config()

    parser = argparse.ArgumentParser(
        description='This is a command-line tool that answers questions using OpenAI or a local model.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 0.4.4'  # Add your version here
    )

    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear the history of questions and answers.'
    )

    parser.add_argument(
        '--set-dev-mode',
        type=str,
        choices=['true', 'false'],
        help='Set dev mode to true or false, which allows or disallows you to use the local model.'
    )

    parser.add_argument(
        'question',
        nargs='*',
        help='Enter the question you want to ask.'
    )

    args = parser.parse_args()

    # If no arguments were passed, print the help message and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.clear:
        clear_history()
        print("FastAsk History cleared.")
        exit()

    if args.set_dev_mode:
        config['dev_mode'] = args.set_dev_mode.lower() == 'true'
        save_config(config)
        print("\033[94mFastAsk Dev mode set to", config['dev_mode'], "\033[0m")
        exit()

    question = ' '.join(args.question)

    history = get_last_n_history(5)

    check_and_run_command(history, question)

    # IF you are devving, you basically just write your own endpoint
    if config['dev_mode']:
        call_dev_mode_router(question)
    else:
        call_the_fastest_endpoint_ever(question)

if __name__ == '__main__':
    main()