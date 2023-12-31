# FastAsk

FastAsk is a Python package that allows you to ask questions and get brief answers quickly. It uses OpenAI's GPT-4 model or a local model to generate responses. You can use it as a command-line utility or integrate it into your own Python projects.

## Installation

FastAsk can be installed using pip:

```bash
pip install fastask
```

## Usage

FastAsk can be used directly from the command line:

```bash
ask "Your question here"
```

For example, if you want to list all items in the current directory sorted by modification time, you can ask:

```bash
ask "list items in dir by date"
```

This will output:

```cli
* `ls -lt`: This command lists all items in the current directory sorted by modification time, newest first.  
* `ls -ltr`: This command lists all items in the current directory sorted by modification time, oldest first.
```

You can also reset the configuration with the `--reset` flag:

```bash
ask --reset
```

## Configuration

FastAsk can be configured to use either OpenAI's GPT-4 model or a local model. The configuration is stored in a `config.ini` file.

To configure FastAsk, run the command with the `--reset` flag:

```bash
ask --reset
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