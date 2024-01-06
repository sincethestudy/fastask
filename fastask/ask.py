#!/usr/bin/env python3

import sys
import os
from openai import OpenAI
import configparser
import inquirer
import argparse
import subprocess
import shlex
import tempfile

current_script_dir = os.path.dirname(os.path.abspath(__file__))
modelfile_path = os.path.join(current_script_dir, "Modelfile")


config = configparser.ConfigParser()

config_path = os.path.expanduser('~/.config/fastask/config.ini')
os.makedirs(os.path.expanduser('~/.config/fastask/'), exist_ok=True)
config.read(config_path)

temp_dir = tempfile.gettempdir()
history_file_path = os.path.join(temp_dir, 'ask_history.txt')


def is_openai_configured():
    if config['OPENAI']['API_KEY'] == '':
        return False
    else:
        return True

def is_configured():
    if 'MODES' in config and 'MODE' in config['MODES']:
        if len(config['MODES']['MODE']) == 0:
            return False

        if config['MODES']['MODE'] == 'OPENAI':
            return is_openai_configured()

        elif config['MODES']['MODE'] == 'LOCAL':
            return True
    else:
        return False

def config_mode():

    questions = [
        inquirer.List('options',
                      message="What do you want to do?",
                      choices=['Use your own OPENAI_API_KEY', 'Use local model with Ollama'],
                      ),
    ]
    answers = inquirer.prompt(questions)

    if answers['options'] == 'Use your own OPENAI_API_KEY':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            api_key = input("Please enter your OpenAI API Key: ")
        config['OPENAI'] = {'API_KEY': api_key}
        config['MODES'] = {'MODE': 'OPENAI'}
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    elif answers['options'] == 'Use local model with Ollama':
        print("Downloading and setting up the local model. This may take a minute or so..")
        try:
            subprocess.check_call(['ollama', '--version'])
            subprocess.run(['ollama', 'create', 'fastask-preset', '-f', modelfile_path])
        except:
            print("Ollama is not installed.")
            print("Please install it following the instructions at:")
            print("\033[4;34mhttps://github.com/jmorganca/ollama\033[0m")
            return
        config['MODES'] = {'MODE': 'LOCAL'}
        with open(config_path, 'w') as configfile:
            config.write(configfile)

def use_openai(client, q):
    history = get_last_n_history(5)  # Get the last 5 entries
    history_prompt = "\n".join(history)

    system_prompt = f"""
You are a command line utility that answers questions quickly and briefly. Don't use any markdown or other formatting. The user is likely looking for a cli command or usage of some tool, attempt to answer the question with just the command that would be relavent, and only if 100% needed, with a single sentence description after the command with a ':'. If there were a few commands you could have given, show them all. Remember that you print to a console, so make it easy to read when possible.

Here is how your responses should look:

**EXAMPLE 1**

<Users Question>
how do i convert image size in ffmpeg

<Your Answer>
`ffmpeg -i input.jpg -filter:v scale=h=1024 output.jpg`: Resizes the image to a height of 1024 pixels.
`ffmpeg -i input.jpg -filter:v scale=w:h=1:1 output.jpg`: Resizes the image to a width and height that are equal, such as 512x512.
`ffmpeg -i input.jpg -filter:v scale=force_original output.jpg`: Resizes the image while preserving its original aspect ratio.

**EXAMPLE 2**

<Users Question>
list items in dir by date

<Your Answer>
`ls -lt`: Lists all items in the current directory sorted by modification time, newest first.  
`ls -ltr`: Lists all items in the current directory sorted by modification time, oldest first.

**EXAMPLE 3**

<Users Question>
how do i make a new docker to run a fresh ubuntu to test on

<Your Answer>
`docker run -it ubuntu`

**EXAMPLE 4**

<Users Question>
how to check disk usage in linux

<Your Answer>
`df -h`: Shows the amount of disk space used and available on Linux file systems.
`du -sh *`: Summarizes the disk usage of each file and directory in the current directory.

**EXAMPLE 5**

<Users Question>
find text in files in linux

<Your Answer>
`grep 'search_text' /path/to/dir/*`: This command searches for 'search_text' within all files in the specified directory.
`grep -r 'search_text' /path/to/dir`: This is the same, but searches recursively.

**EXAMPLE 6**

<Users Question>
how to change file permissions in linux

<Your Answer>
`chmod 755 filename`: This command changes the permissions of 'filename' to 'rwxr-xr-x' (read, write, and execute for owner, read and execute for group and others).
`chmod u+x filename`: This command adds execute permission for the user (owner) of 'filename'.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Answer this as briefly as possible: " + q},
    ]

    if history:
        messages.insert(1, {"role": "user", "content": "For context, here are recent question and answers, so if the current question is ambigous see if theres context here.\n\n" + history_prompt})

    completion_stream = client.chat.completions.create(
        messages=messages,
        model="gpt-4-1106-preview",
        stream=True,
    )

    response = ""
    for chunk in completion_stream:
        response += chunk.choices[0].delta.content or ""
        print(chunk.choices[0].delta.content or "", end="")

    print()
    print()
    add_to_history(q, response)

def use_local(q):
    history = get_last_n_history(5)  # Get the last 5 entries
    history_prompt = "\n".join(history)

    command = ['ollama', 'run', 'fastask-preset', q]
    if history:
        command = ['ollama', 'run', 'fastask-preset', "For context, here are recent question and answers\n\n" + history_prompt + "\n\n" + q]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)

    output = ""
    while True:
        char = process.stdout.read(1)
        if not char:  # End of output
            break
        print(char, end='')  # print to stdout in real-time
        output += char  # capture output

    process.stdout.close()
    process.wait()

    add_to_history(q, output) 

def add_to_history(question, answer):
    with open(history_file_path, 'a') as f:
        f.write(f"Question: {question}\nAnswer: {answer}\n\n")

    # Check if history has more than 10 entries
    with open(history_file_path, 'r') as f:
        lines = f.readlines()
    blocks = "".join(lines).split("\n\n")[:-1]  # Split by empty lines
    if len(blocks) > 10:
        # Delete the oldest entry
        with open(history_file_path, 'w') as f:
            f.write("\n\n".join(blocks[1:]) + "\n\n")

def get_last_n_history(n):
    # Check if the file exists, if not, create it
    if not os.path.exists(history_file_path):
        with open(history_file_path, 'w') as f:
            pass

    with open(history_file_path, 'r') as f:
        lines = f.readlines()

    blocks = "".join(lines).split("\n\n")[:-1]  # Split by empty lines
    return blocks[-n:]

def clear_history():
    if os.path.exists(history_file_path):
        os.remove(history_file_path)
    with open(history_file_path, 'w') as f:
        pass  # Create the file if it doesn't exist


def main():

    parser = argparse.ArgumentParser(
        description='This is a command-line tool that answers questions using OpenAI or a local model.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--reset', 
        action='store_true', 
        help='Reset the configuration to its default state.'
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

    if args.reset:
        config_mode()
        exit()

    if args.clear:
        clear_history()
        print("FastAsk History cleared.")
        exit()
    
    question = shlex.join(args.question)  # Change this line

    if not is_configured():
        config_mode()

        return

    if config['MODES']['MODE'] == 'OPENAI':
        client = OpenAI(
            api_key=config['OPENAI']['API_KEY'],
        )
        use_openai(client, question)

    elif config['MODES']['MODE'] == 'LOCAL':
        use_local(question)

if __name__ == '__main__':
    main()