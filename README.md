# Strix

Strix is a command-line penetration testing assistant powered by AI. It integrates with various AI models to help cybersecurity professionals and enthusiasts with technical tasks, while maintaining strict security controls to prevent unintended actions.

![Strix](https://strixproject.github.io/Strix.png)

## Features

- **Multi-AI Support**: Works with Google Gemini, OpenAI GPT-4, Anthropic Claude, Groq LLaMA 3, and Mistral
- **Expanded Model Selection**: Access to multiple models from each provider (e.g., gemini-2.5-flash, gpt-4o, claude-3-opus, etc.)
- **Tool Integration**: Built-in functions for common pentesting tools (nmap, subfinder, gobuster, etc.)
- **Interactive Mode**: Real-time conversation interface with the AI assistant
- **Enhanced UX**: Improved user experience with prompt_toolkit for better input handling
- **Confirmation Prompts**: Asks for confirmation before executing dangerous commands
- **Auto-Save Mode**: Optional bypass for experienced users

## What's New in v0.1.2

- **Bug Fixes**: Resolved several stability issues and bugs from previous version
- **Performance Improvements**: Enhanced response times and overall application performance
- **UI Enhancements**: Minor user interface improvements for better user experience

## What's New in v0.1.1

- **Expanded Model Support**: Added support for multiple models from each AI provider
  - **Google Gemini**: gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-pro-exp, gemini-1.0-pro
  - **OpenAI**: gpt-4, gpt-4-turbo, gpt-4o, gpt-3.5-turbo
  - **Anthropic**: claude-3-sonnet, claude-3-opus, claude-3-haiku, claude-2.1
  - **Groq**: llama3-70b-8192, llama-3.1-8b, llama-3.1-70b, mixtral-8x7b, gemma-7b
  - **Mistral**: mistral-small-latest, mistral-large, mistral-medium, mistral-nemo
- **Enhanced User Experience**: Improved input handling using prompt_toolkit with better formatting and interaction
- **Better Model Selection Menu**: Organized and expanded model selection interface

## Installation

```bash
# Clone the repository
git clone https://github.com/strixproject/Strix.git
cd strix

# Option 1: Install in virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e . # Or pipx install -e .

# Option 2: Install globally/local (without virtual environment)
pip install -e . # Or pipx install -e .

# If the binary is in ~/.local/share/pipx/venvs/strix/bin/strix
sudo ln -sf ~/.local/share/pipx/venvs/strix/bin/strix /usr/local/bin/strix

# Set up API keys
# Create ~/Strix/.env with your API keys:
# GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# GROQ_API_KEY=your_groq_api_key_here
# MISTRAL_API_KEY=your_mistral_api_key_here
```

## Usage

```bash
# Start interactive mode
strix

# Start with auto-save mode (bypass confirmation prompts)
strix --auto-save

# Start with a specific system prompt
strix --prompt ctf
strix --prompt vuln-research

# Show help
strix --help
```

## System Prompts

Strix comes with three built-in system prompts that can be selected using the `--prompt` option:

### Pentesting Assistant (Default)

```bash
strix --prompt pentest
```

```
Rules:
1. NEVER save scan results to a file automatically.
2. ONLY save to a file if the user explicitly asks (e.g., "save to file.txt" or "write this to output.txt").
3. When scanning (subdomains, ports, web), show output in the terminal only.
4. If the user provides a list and says "save to X", use 'write_file' with that content.
5. Be precise, technical, and do not hallucinate actions.
6. Match the user's language.
7. Use markdown: **bold**, *italic*, * lists.
8. You can create any script according to user requests, and can save the script via the save file function.
```

### CTF Assistant

```bash
strix --prompt ctf
```

```
Rules:
1. Help users solve CTF challenges ethically and educationally.
2. Break down complex problems into understandable steps.
3. Explain methodologies and reasoning clearly.
4. Suggest multiple approaches when applicable.
5. Point out common pitfalls and how to avoid them.
6. Encourage learning and understanding over quick solutions.
7. Respect challenge categories (crypto, forensics, web, etc.).
```

### Vulnerability Researcher

```bash
strix --prompt vuln-research
```

```
Rules:
1. Assist with vulnerability analysis and research methodologies.
2. NEVER exploit vulnerabilities in real systems without authorization.
3. Explain vulnerability concepts with practical examples.
4. Guide users through secure coding practices.
5. Help with CVE analysis and PoC development in controlled environments.
6. Provide guidance on responsible disclosure procedures.
7. Detail attack vectors and mitigation strategies.
8. Emphasize ethical considerations in all recommendations.
```

## Supported AI Models

### Google Gemini
- gemini-2.5-flash (default)
- gemini-2.0-flash
- gemini-1.5-pro
- gemini-1.5-pro-exp
- gemini-1.0-pro

### OpenAI
- gpt-4
- gpt-4-turbo
- gpt-4o
- gpt-3.5-turbo

### Anthropic Claude
- claude-3-sonnet
- claude-3-opus
- claude-3-haiku
- claude-2.1

### Groq
- llama3-70b-8192
- llama-3.1-8b
- llama-3.1-70b
- mixtral-8x7b
- gemma-7b

### Mistral
- mistral-small-latest
- mistral-large
- mistral-medium
- mistral-nemo

## Required Tools

For full functionality, install these security tools:
- subfinder
- nmap
- gobuster
Or you can use your local tools that are already installed.

## Documentation

Model selection

![doc](https://strixproject.github.io/1.png)


Running Tools

![doc](https://strixproject.github.io/2.png)


Write Scripts

![doc](https://strixproject.github.io/3.png)


## License

MIT License - see LICENSE file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
