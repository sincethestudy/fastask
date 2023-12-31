# file: ask.py
import sys
import os
from openai import OpenAI
import configparser
import inquirer
import argparse
import subprocess
import shlex

config = configparser.ConfigParser()
config.read('config.ini')

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

        elif config['MODES']['MODE'] == 'GLOBE':
            return True

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
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    elif answers['options'] == 'Use local model with Ollama':
        print("Downloading and setting up the local model. This may take a minute or so..")
        try:
            subprocess.check_call(['ollama', '--version'])
            subprocess.run(['ollama', 'create', 'fastask-preset', '-f', './Modelfile'])
        except subprocess.CalledProcessError:
            print("Ollama is not installed. Please install it following the instructions at https://github.com/jmorganca/ollama?tab=readme-ov-file#:~:text=MIT%20license-,Ollama,-Get%20up%20and")
            return
        config['MODES'] = {'MODE': 'LOCAL'}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

def use_openai(client, q):
    system_prompt = """
You are a command line utility that answers questions quickly and briefly. Don't use any markdown or other formatting. The user is likely looking for a cli command or usage of some tool, attempt to answer the question with just the command that would be relavent, and only if 100% needed, with a single sentence. If you give the user a command, give a brief explanation of what it does. If there were a few commands you could have given, show them all, and explain the difference between them. Remember that you print to a console, so make it easy to read when possible.

Here are some example of good answers:

***EXAMPLE 1***

Users Question: 
converting image size ffmpeg

Your Answer:
* `ffmpeg -i input.jpg -filter:v scale=h=1024 output.jpg`: This command resizes the image to a height of 1024 pixels.
* `ffmpeg -i input.jpg -filter:v scale=w:h=1:1 output.jpg`: This command resizes the image to a width and height that are equal, such as 512x512.
* `ffmpeg -i input.jpg -filter:v scale=force_original output.jpg`: This command resizes the image while preserving its original aspect ratio.

***EXAMPLE 2***

Users Question:
list items in dir by date

Your Answer:
* `ls -lt`: This command lists all items in the current directory sorted by modification time, newest first.  
* `ls -ltr`: This command lists all items in the current directory sorted by modification time, oldest first.

Most important, dont talk, just go.
"""

    completion_stream = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Answer this as briefly as possible: " + q},
    ],
    model="gpt-4-1106-preview",
    stream=True,
    )

    print()
    for chunk in completion_stream:
        print(chunk.choices[0].delta.content or "", end="")

    print()
    print()

def use_local(q):
    subprocess.run(['ollama', 'run', 'fastask-preset', q])

def main():
    parser = argparse.ArgumentParser(description='Your description here')
    parser.add_argument('--reset', action='store_true', help='Reset the configuration')
    parser.add_argument('question', nargs='*', help='Your question here')  # Add this line
    args = parser.parse_args()

    if args.reset:
        config_mode()
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