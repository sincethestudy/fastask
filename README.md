# FastAsk

https://www.fastask.ai/


FastAsk is a Python package that allows you to ask questions and get brief answers quickly. It uses OpenAI's GPT-3.5 model hosted on my own endpoint, for free. You can use it as a command-line utility.

Logs are saved, and may be used for fine tuning in the future.

## Installation


FastAsk can be installed using pip:

```bash
pip install fastask
```

## Usage

FastAsk can be used directly from the command line:

```bash
>>> ask list items in dir by date
* `ls -lt`: This command lists all items in the current directory sorted by modification time, newest first.  
* `ls -ltr`: This command lists all items in the current directory sorted by modification time, oldest first.
```

More examples:

```bash
>>> ask find ip address
* `curl ifconfig.me`: This command fetches your public IP address.
* `ip addr show`: This command shows your local IP address.
```

```bash
>>> ask "convert video to audio using ffmpeg"
* `ffmpeg -i input.mp4 -vn -ab 320k -ar 44100 -y output.mp3`: This command converts a video file (input.mp4) to an audio file (output.mp3) using ffmpeg.
```

## License

FastAsk is licensed under the MIT License. See the `LICENSE` file for more details.
