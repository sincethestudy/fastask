# FastAsk

FastAsk is a Python package that allows you to ask questions and get brief answers quickly. It uses OpenAI's GPT-4 model or a local model to generate responses. You can use it as a command-line utility.

## Installation


FastAsk can be installed using pip:

```bash
pip install fastask
```

## Usage

FastAsk can be used directly from the command line:

```bash
>>> ask "list items in dir by date"
* `ls -lt`: This command lists all items in the current directory sorted by modification time, newest first.  
* `ls -ltr`: This command lists all items in the current directory sorted by modification time, oldest first.
```

More examples:

```bash
>>> ask "find ip address"
* `curl ifconfig.me`: This command fetches your public IP address.
* `ip addr show`: This command shows your local IP address.
```

```bash
>>> ask "convert video to audio using ffmpeg"
* `ffmpeg -i input.mp4 -vn -ab 320k -ar 44100 -y output.mp3`: This command converts a video file (input.mp4) to an audio file (output.mp3) using ffmpeg.
```

## Configuration

FastAsk can be configured to use either OpenAI's GPT-4 model or a local model. The configuration is stored in a `config.ini` file.

To configure FastAsk, run the command with the `--reset` flag:

```bash
>>> ask --reset
```

You will be prompted to choose between using your own OpenAI API key or a local model with Ollama. If you choose to use your own OpenAI API key, you will be asked to enter it.

## Local Model

If you choose to use a local model with Ollama, FastAsk will download and set up the local model. This may take a few minutes. If Ollama is not installed, you will be given instructions on how to install it.

## OpenAI Model

If you choose to use your own OpenAI API key, you will need to enter it when prompted. The API key is stored in the `config.ini` file and is used to authenticate with the OpenAI API.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue to discuss any changes you would like to make.

## License

FastAsk is licensed under the MIT License. See the `LICENSE` file for more details.
