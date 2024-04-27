import sys
import os
import argparse
import json

from .history import History
from .config import Config
from .llm import askLLM

history_manager = History()
config_manager = Config()

def check_and_run_command(history, question):
    if question.lower() == 'history':
        history = history_manager.get(1)
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
        history = history_manager.get(5)

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


def main():
    config = config_manager.load()

    parser = argparse.ArgumentParser(
        description='This is a command-line tool that answers questions using OpenAI or a local model.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 0.4.6'  # Add your version here
    )

    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear the history of questions and answers.'
    )

    parser.add_argument(
        '--llm',
        type=str,
        choices=['fastask', 'fastask-local', 'azure', 'groq', 'openai', 'togetherai'],
        help='Select the large language model to use. Default is fastask. All other models and are intended for developer use and require API keys.'
    )
    
    parser.add_argument(
        '--enable-leaderboard',
        type=bool,
        default=False,
        help='Enable the leaderboard.'
    )

    parser.add_argument(
        '--set-user',
        type=str,
        help='Specify a custom config file to use.'
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
        history_manager.clear_history()
        print("FastAsk History cleared.")
        exit()
        
    if args.enable_leaderboard:
        config['enable_leaderboard'] = True
        config_manager.save(config)
        print("\033[92mLeaderboard enabled.\033[0m")
        exit()
        
    if args.set_user:
        config['user'] = args.set_user
        config_manager.save(config)
        print("\033[92mUser set to", config['user'], "\033[0m")
        exit()

    # use fastask as llm by default if no llm is set
    try:
        llm = config['llm']
    except:
        config['llm'] = 'fastask'
        config_manager.save(config)


    if args.llm:
        config['llm'] = args.llm.lower()
        config_manager.save(config)
        print("\033[94mFastAsk LLM set to", config['llm'], "\033[0m")
        exit()

    question = ' '.join(args.question)
    history = history_manager.get(5)
    check_and_run_command(history, question)
    askLLM(question, config['llm'])
        

if __name__ == '__main__':
    main()
