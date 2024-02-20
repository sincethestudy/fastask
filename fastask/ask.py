import sys
import os
import argparse
import tempfile
import platform
import json
import requests

from .version import __version__

temp_dir = tempfile.gettempdir()
history_file_path = os.path.join(temp_dir, 'ask_history.json')

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

    # response = requests.post(url="http://0.0.0.0:8080/itsfast", json={"messages": messages}).json()
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

def check_and_run_command(history, question):
    # Check if the question can be converted to an integer
    try:
        index = int(question)
        history = get_last_n_history(5)

        if history:
            answer = history[-1]["Answer"]
            answer_json = json.loads(answer)
            if index <= len(answer_json):
                command = answer_json[index-1]["command"]
                os.system(command)
            else:
                print("No command at this index in the answer.")
        else:
            print("No history available.")
        exit()
    except ValueError:
        pass  # The question is not an integer, so we treat it as a question



def main():

    parser = argparse.ArgumentParser(
        description='This is a command-line tool that answers questions using OpenAI or a local model.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 0.3.6'  # Add your version here
    )

    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear the history of questions and answers.'
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

    question = ' '.join(args.question)


    history = get_last_n_history(5)

    check_and_run_command(history, question)

    call_the_fastest_endpoint_ever(question)

if __name__ == '__main__':
    main()
