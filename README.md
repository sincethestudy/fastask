
# FastAsk

[Fastask.ai](https://www.fastask.ai/)


FastAsk is a the fastest way to get answers in the command line. 

By default, requests are routed through a freely hosted LLM endpoint so users can start asking right away.

However, its very easy to clone this and run whatever LLM you want, we have prebuilt examples for you to use your own Groq, Togetherai or OpenAI key!

## Installation


FastAsk can be installed using pip:

```bash
pip install fastask
```

## Usage

FastAsk can be used directly from the command line:

```bash
>>> ask list items in dir by date
1. 'ls -lt' - List newer first
2. 'ls -ltr' - List older first
```

More examples:

```bash
>>> ask find ip address
1. 'ipconfig getifaddr en0' - Get IP for en0
2. 'ifconfig | grep 'inet '' - List all IPs
3. 'curl ifconfig.me' - Get public IP
```

```bash
>>> ask "convert video to audio using ffmpeg"
1. 'ffmpeg -i video.mp4 audio.mp3' - Convert to MP3
2. 'ffmpeg -i video.mp4 -vn audio.ogg' - Convert to OGG
3. 'ffmpeg -i video.mp4 -q:a 0 audio.wav' - Convert to WAV
```

## Running Commands

```bash
>>> ask <number>
```

you can run the commands it outputs like so:

```bash
>>> ask how to ping google
1. 'ping google.com' - Default ping Google.

>>> ask 1
PING google.com (142.251.41.78): 56 data bytes
64 bytes from 142.251.41.78: icmp_seq=0 ttl=112 time=7.765 ms
...
```


## History
FastAsk stores the past 5 commands you asked, and the responses so you can refer to previous commands and outputs easily.

Example:

```bash
>>> ask how to find installed packages
1. 'brew list' - List on macOS with Homebrew.
```

and then a second query can be like:

```bash
>>> ask in python
1. 'pip list' - List for pip packages.
2. 'conda list' - List for conda envs.
```

you can also re-print the last output fastask gave with:

```bash
>>> ask history
1. 'pip list' - List for pip packages.
2. 'conda list' - List for conda envs.
```


If something weird is occuring/having weird errors, try clearing your history.

```bash
>>> ask --clear
FastAsk History Cleared.
```

## Notes

if you come across something that looks like this
```bash
>>> ask what is rebase?
zsh: no matches found: rebase?
```

its because of how args are parsed in the actual zsh/bash itself. If you want to put a question mark or any other of: `-,./;'][-=` you have to wrap your question in qoutes like:
```bash
>>> ask "what is rebase?"
```

## Developing Locally

To make edits to fastask:

1. Clone this repo
```bash
git clone https://github.com/sincethestudy/fastask.git
```

2. Go to the root folder
```bash
cd fastask
```

3. pip install it in that directory with `"editable"` mode on on so that any changes you make automatically update the package on your system without having to install every time. 

Make sure to uninstall fastask before you do this if you've already installed it before.
```bash
(if needed) pip uninstall fastask
```

```bash
pip install -e .
```

Now you can edit the source code and still use the `ask` CLI command anywhere in your system on your own custom version of fastask.

## Making your own LLM endpoint

We really want users to mess around and see how they can improve FastAsk. 

There is a `dev_mode_router.py` file which is essentially a playground file for you to write your own endpoint function. 

To switch from using the default external server LLM:

```bash
>>>ask --set-dev-mode=true
```

and to go back:

```bash
>>>ask --set-dev-mode=false
```

When `set-dev-mode` is set to True, it routes the question to the `dev_endpoint` in `dev_mode_router.py`, and you are expected to modify that function however you desire.

Currently there are a few already implemented functions, you can just uncomment any of them to try (make sure you've set the env var). 

```python
/src/fastask/dev_mode_router.py
line 160

# response = requests.post(url="https://fastask.fly.dev/itsfast", json={"messages": messages}).json()
# response = requests.post(url="http://0.0.0.0:8080/itsfast", json={"messages": messages}).json()
response  =  GROQ_client(messages)
# response = AZURE_client(messages)
# response = OPENAI_client(messages)
# response = TOGETHERAI_client(messages)
```


You can add others, for example, adding a `OLLAMA_client` would be a good next step.



## Environment Variables for Dev Mode

You need to set the environment variables in the `.env` for each of those clients that you plan on using (or if you make your own). 

There is a `.env.example` in this repo, just copy the contents into a new `.env` file and populate the keys you need.

## License

FastAsk is licensed under the MIT License. See the `LICENSE` file for more details.
