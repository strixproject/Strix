import os
import sys
import subprocess
import json
import argparse
import re
import time
import threading
from dotenv import load_dotenv
import google.generativeai as genai

try:
    from colorama import init as colorama_init, Fore, Back, Style
    colorama_init(autoreset=True)
except Exception:
    class _F:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class _B:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class _S:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""
    Fore, Back, Style = _F(), _B(), _S()
    def colorama_init(autoreset=True): pass

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import confirm


PALETTE = {
    "accent": Fore.CYAN + Style.BRIGHT,
    "muted": Fore.WHITE + Style.DIM,
    "success": Fore.GREEN + Style.BRIGHT,
    "placeholder": Fore.BLACK + Style.DIM,
    "error": Fore.RED + Style.BRIGHT,
    "command": Fore.YELLOW + Style.NORMAL,
    "banner_bg": Back.MAGENTA,
    "user_input": Fore.MAGENTA + Style.BRIGHT,
    "ai_response": Fore.CYAN + Style.NORMAL,
    "tool_call": Fore.YELLOW + Style.DIM,
    "tool_output": Fore.BLUE + Style.BRIGHT,
    "reset": Style.RESET_ALL
}


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


def get_yes_no_input(message: str) -> bool:
    """Get yes/no input using prompt_toolkit with proper color support"""
    try:
        from prompt_toolkit.formatted_text import ANSI
        colored_message = ANSI(message)
        return confirm(colored_message)
    except ImportError:
        return input(message).strip().lower() in ['y', 'yes']


def get_text_input(prompt_text: str) -> str:
    """Get text input using prompt_toolkit with proper color support"""
    try:
        from prompt_toolkit.formatted_text import ANSI
        colored_prompt = ANSI(prompt_text)
        return prompt(colored_prompt).strip()
    except ImportError:
        return input(prompt_text).strip()


def ensure_env_file():
    env_path = os.path.expanduser("~/Strix/.env")


    os.makedirs(os.path.dirname(env_path), exist_ok=True)


    if not os.path.exists(env_path):
        print(PALETTE["accent"] + f"\nCreating .env file at: {env_path}" + PALETTE["reset"])
        with open(env_path, 'w') as f:
            f.write("# Strix AI Configuration File\n")
            f.write("# Add your API keys below\n")
            f.write("# GOOGLE_API_KEY=your_google_api_key_here\n")
            f.write("# OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("# ANTHROPIC_API_KEY=your_anthropic_api_key_here\n")
            f.write("# GROQ_API_KEY=your_groq_api_key_here\n")
            f.write("# MISTRAL_API_KEY=your_mistral_api_key_here\n")
            f.write("# TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here\n")
        print(PALETTE["success"] + f"Empty .env file created. Please add your API keys to {env_path}" + PALETTE["reset"])

    return env_path


def select_ai_model():

    ensure_env_file()


    env_path = os.path.expanduser("~/Strix/.env")


    load_dotenv(env_path, override=True)
    model_choice = os.getenv("STRIX_MODEL_CHOICE")

    if model_choice and model_choice != "":
        print(PALETTE["accent"] + f"\nUsing saved model choice: {model_choice}" + PALETTE["reset"])

        model_map = {
            "1": ("gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.5-flash"),
            "11": ("gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.0-flash"),
            "12": ("gemini", os.getenv("GOOGLE_API_KEY"), "gemini-1.5-pro"),
            "13": ("gemini", os.getenv("GOOGLE_API_KEY"), "gemini-1.5-pro-exp"),
            "14": ("gemini", os.getenv("GOOGLE_API_KEY"), "gemini-1.0-pro"),

            "2": ("openai", os.getenv("OPENAI_API_KEY"), "gpt-4"),
            "21": ("openai", os.getenv("OPENAI_API_KEY"), "gpt-4-turbo"),
            "22": ("openai", os.getenv("OPENAI_API_KEY"), "gpt-4o"),
            "23": ("openai", os.getenv("OPENAI_API_KEY"), "gpt-3.5-turbo"),

            "3": ("anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-sonnet"),
            "31": ("anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-opus"),
            "32": ("anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-haiku"),
            "33": ("anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-2.1"),

            "4": ("groq", os.getenv("GROQ_API_KEY"), "llama3-70b-8192"),
            "41": ("groq", os.getenv("GROQ_API_KEY"), "llama-3.1-8b"),
            "42": ("groq", os.getenv("GROQ_API_KEY"), "llama-3.1-70b"),
            "43": ("groq", os.getenv("GROQ_API_KEY"), "mixtral-8x7b"),
            "44": ("groq", os.getenv("GROQ_API_KEY"), "gemma-7b"),

            "5": ("mistral", os.getenv("MISTRAL_API_KEY"), "mistral-small-latest"),
            "51": ("mistral", os.getenv("MISTRAL_API_KEY"), "mistral-large"),
            "52": ("mistral", os.getenv("MISTRAL_API_KEY"), "mistral-medium"),
            "53": ("mistral", os.getenv("MISTRAL_API_KEY"), "mistral-nemo"),
        }

        if model_choice in model_map:
            return model_map[model_choice]
        else:
            return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.5-flash"

    print(PALETTE["accent"] + "\nSelect AI Model:" + PALETTE["reset"])

    print("\n[1]  Google Gemini")
    print("     1. gemini-2.5-flash (default)")
    print("     11. gemini-2.0-flash")
    print("     12. gemini-1.5-pro")
    print("     13. gemini-1.5-pro-exp")
    print("     14. gemini-1.0-pro")

    print("\n[2]  OpenAI")
    print("     2. gpt-4")
    print("     21. gpt-4-turbo")
    print("     22. gpt-4o")
    print("     23. gpt-3.5-turbo")

    print("\n[3]  Anthropic")
    print("     3. claude-3-sonnet")
    print("     31. claude-3-opus")
    print("     32. claude-3-haiku")
    print("     33. claude-2.1")

    print("\n[4]  Groq")
    print("     4. llama3-70b-8192")
    print("     41. llama-3.1-8b")
    print("     42. llama-3.1-70b")
    print("     43. mixtral-8x7b")
    print("     44. gemma-7b")

    print("\n[5]  Mistral")
    print("     5. mistral-small-latest")
    print("     51. mistral-large")
    print("     52. mistral-medium")
    print("     53. mistral-nemo")

    choice = input("\nEnter choice (e.g., 1 for gemini-2.5-flash, 22 for gpt-4o) [default: 1]: ").strip() or "1"


    with open(env_path, 'a') as f:
        f.write(f"\nSTRIX_MODEL_CHOICE={choice}\n")

    if choice in ["11", "12", "13", "14"]:
        if choice == "11":
            return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.0-flash"
        elif choice == "12":
            return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-1.5-pro"
        elif choice == "13":
            return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-1.5-pro-exp"
        elif choice == "14":
            return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-1.0-pro"
        else:
            return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.5-flash"
    elif choice in ["2", "21", "22", "23"]:
        if choice == "21":
            return "openai", os.getenv("OPENAI_API_KEY"), "gpt-4-turbo"
        elif choice == "22":
            return "openai", os.getenv("OPENAI_API_KEY"), "gpt-4o"
        elif choice == "23":
            return "openai", os.getenv("OPENAI_API_KEY"), "gpt-3.5-turbo"
        else:
            return "openai", os.getenv("OPENAI_API_KEY"), "gpt-4"
    elif choice in ["3", "31", "32", "33"]:
        if choice == "31":
            return "anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-opus"
        elif choice == "32":
            return "anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-haiku"
        elif choice == "33":
            return "anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-2.1"
        else:
            return "anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-sonnet"
    elif choice in ["4", "41", "42", "43", "44"]:
        if choice == "41":
            return "groq", os.getenv("GROQ_API_KEY"), "llama-3.1-8b"
        elif choice == "42":
            return "groq", os.getenv("GROQ_API_KEY"), "llama-3.1-70b"
        elif choice == "43":
            return "groq", os.getenv("GROQ_API_KEY"), "mixtral-8x7b"
        elif choice == "44":
            return "groq", os.getenv("GROQ_API_KEY"), "gemma-7b"
        else:
            return "groq", os.getenv("GROQ_API_KEY"), "llama3-70b-8192"
    elif choice in ["51", "52", "53"]:
        if choice == "51":
            return "mistral", os.getenv("MISTRAL_API_KEY"), "mistral-large"
        elif choice == "52":
            return "mistral", os.getenv("MISTRAL_API_KEY"), "mistral-medium"
        elif choice == "53":
            return "mistral", os.getenv("MISTRAL_API_KEY"), "mistral-nemo"
        else:
            return "mistral", os.getenv("MISTRAL_API_KEY"), "mistral-small-latest"
    else:
        return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.5-flash"

def validate_api_key(ai_type, api_key):
    if not api_key or api_key.strip() == "":
        print(PALETTE["error"] + f"\nError: {ai_type.upper()}_API_KEY not found in .env file." + PALETTE["reset"])
        print(PALETTE["muted"] + f"Please add your {ai_type} API key to ~/Strix/.env file." + PALETTE["reset"])
        print(PALETTE["muted"] + "Example: " + ai_type.upper() + "_API_KEY=your_api_key_here" + PALETTE["reset"])
        

        setup_choice = "y" if get_yes_no_input(PALETTE["accent"] + "\nWould you like to add your API key now? (y/N): " + PALETTE["reset"]) else "n"
        
        if setup_choice == 'y':
            api_key_value = get_text_input(f"Enter your {ai_type} API key: ")
            if api_key_value:

                env_path = os.path.expanduser("~/Strix/.env")
                with open(env_path, 'a') as f:
                    f.write(f"\n{ai_type.upper()}_API_KEY={api_key_value}\n")
                
                print(PALETTE["success"] + f"API key added to {env_path}. Please restart the application." + PALETTE["reset"])
                sys.exit(0)
            else:
                print(PALETTE["error"] + "No API key provided. Exiting." + PALETTE["reset"])
                sys.exit(1)
        else:
            print(PALETTE["error"] + "No API key provided. Exiting." + PALETTE["reset"])
            sys.exit(1)

def initialize_ai():
    ai_type, API_KEY, MODEL = select_ai_model()
    validate_api_key(ai_type, API_KEY)

    if ai_type == "gemini":
        genai.configure(api_key=API_KEY)
        return ai_type, API_KEY, MODEL
    elif ai_type == "openai":
        try:
            import openai
            client = openai.OpenAI(api_key=API_KEY)
            return ai_type, API_KEY, MODEL
        except ImportError:
            print(PALETTE["error"] + "Error: openai package not installed. Run 'pip install openai'" + PALETTE["reset"])
            sys.exit(1)
    elif ai_type == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=API_KEY)
            return ai_type, API_KEY, MODEL
        except ImportError:
            print(PALETTE["error"] + "Error: anthropic package not installed. Run 'pip install anthropic'" + PALETTE["reset"])
            sys.exit(1)
    elif ai_type == "groq":
        try:
            import groq
            client = groq.Groq(api_key=API_KEY)
            return ai_type, API_KEY, MODEL
        except ImportError:
            print(PALETTE["error"] + "Error: groq package not installed. Run 'pip install groq'" + PALETTE["reset"])
            sys.exit(1)
    elif ai_type == "mistral":
        try:
            import mistralai
            from mistralai.client import MistralClient
            client = MistralClient(api_key=API_KEY)
            return ai_type, API_KEY, MODEL
        except ImportError:
            print(PALETTE["error"] + "Error: mistralai package not installed. Run 'pip install mistralai'" + PALETTE["reset"])
            sys.exit(1)


def define_tools():
    run_command_func = genai.protos.FunctionDeclaration(
        name="run_command", description="Execute a generic terminal command.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={"command": genai.protos.Schema(type=genai.protos.Type.STRING, description="Command to execute.")}, required=["command"])
    )
    scan_subdomains_func = genai.protos.FunctionDeclaration(
        name="scan_subdomains", description="Enumerate subdomains using 'subfinder'. Output is shown in terminal (not saved automatically).",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={"domain": genai.protos.Schema(type=genai.protos.Type.STRING, description="Target domain (e.g. example.com).")}, required=["domain"])
    )
    scan_ports_func = genai.protos.FunctionDeclaration(
        name="scan_ports", description="Scan all ports with version detection using 'nmap'. Output is shown in terminal.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={"target": genai.protos.Schema(type=genai.protos.Type.STRING, description="Target IP or domain.")}, required=["target"])
    )
    enum_web_func = genai.protos.FunctionDeclaration(
        name="enum_web", description="Enumerate web directories using 'gobuster'. Output is shown in terminal.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={"url": genai.protos.Schema(type=genai.protos.Type.STRING, description="Target URL.")}, required=["url"])
    )
    read_file_func = genai.protos.FunctionDeclaration(
        name="read_file", description="Read contents of a text file.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={"path": genai.protos.Schema(type=genai.protos.Type.STRING, description="Full path to the file.")}, required=["path"])
    )
    write_file_func = genai.protos.FunctionDeclaration(
        name="write_file", description="Write content to a file.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={"path": genai.protos.Schema(type=genai.protos.Type.STRING, description="Full path to the file."), "content": genai.protos.Schema(type=genai.protos.Type.STRING, description="Content to write.")}, required=["path", "content"])
    )
    list_files_func = genai.protos.FunctionDeclaration(
        name="list_files", description="List all files and directories in the current working directory.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
    )
    clear_screen_func = genai.protos.FunctionDeclaration(
        name="clear_screen", description="Clear the terminal screen.",
        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={})
    )

    return genai.protos.Tool(
        function_declarations=[
            run_command_func, scan_subdomains_func, scan_ports_func,
            enum_web_func, read_file_func, write_file_func,
            list_files_func, clear_screen_func
        ]
    )


def run_command(command: str, auto_save: bool = False) -> str:
    if not command or len(command.strip()) == 0:
        return "Error: Empty command provided."

    dangerous_patterns = [';', '&&', '||', '|', '`', '$(', '>', '<', '>>', '>>>', ';&', ';&;']
    for pattern in dangerous_patterns:
        if pattern in command:
            return f"Error: Command contains potentially dangerous pattern: {pattern}"

    if '..' in command or command.startswith('/') or command.startswith('../'):
        return "Error: Command contains invalid path pattern."

    if not auto_save:
        print(PALETTE["command"] + "\n[AI PROPOSED COMMAND]\n  $ " + command + "\n" + PALETTE["reset"])
        confirmation = "y" if get_yes_no_input("Are you sure you want to execute this command? [y/N]: ") else "n"
        if confirmation != 'y':
            return "Command cancelled by user."
    else:
        print(PALETTE["muted"] + f"\n[AUTO-SAVE MODE ON] Executing: $ {command}" + PALETTE["reset"])

    try:
        import shlex
        cmd_parts = shlex.split(command)
        result = subprocess.run(cmd_parts, check=True, text=True, capture_output=True, encoding='utf-8')
        stdout, stderr = result.stdout or "", result.stderr or ""
        combined = stdout + ("\n[STDERR]\n" + stderr if stderr else "")
        return combined.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: Command failed. Exit code {e.returncode}.\nStderr: {e.stderr}"
    except ValueError as e:
        return f"Error: Invalid command format: {e}"
    except Exception as e:
        return f"Error occurred: {e}"

def scan_subdomains(domain: str, auto_save: bool = False) -> str:
    return run_command(f"subfinder -d {domain} -silent", auto_save)

def scan_ports(target: str, auto_save: bool = False) -> str:
    return run_command(f"nmap -sV -p- {target}", auto_save)

def enum_web(url: str, auto_save: bool = False) -> str:
    wordlist_path = os.getenv("GOBUSTER_WORDLIST", "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")
    return run_command(f"gobuster dir -u {url} -w {wordlist_path} -x php,txt,bak,html -t 50", auto_save)

def read_file(path: str) -> str:
    max_file_size = 1 * 1024 * 1024
    try:
        if os.path.getsize(path) > max_file_size:
            return f"Error: File '{path}' is too large."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at path '{path}'."
    except Exception as e:
        return f"Error: Cannot read file '{path}'. {e}"

def write_file(path: str, content: str, auto_save: bool = False) -> str:
    if not auto_save:
        lines = content.splitlines()
        preview_lines = 20
        content_preview = "\n".join(lines[:preview_lines])
        if len(lines) > preview_lines:
            content_preview += f"\n... (and {len(lines) - preview_lines} more lines)"

        print(PALETTE["command"] + f"\n[AI PROPOSED WRITE]\n  Path: {path}" + PALETTE["reset"])

        bubble_content = f"Content preview:\n{content_preview}"
        print(format_chat_bubble(bubble_content, "File Content Preview"))

        confirmation = "y" if get_yes_no_input("Are you sure you want to write this file? [y/N]: ") else "n"
        if confirmation != 'y':
            return "File write cancelled by user."
    else:
        print(PALETTE["muted"] + f"\n[AUTO-SAVE MODE ON] Writing to file: {path}" + PALETTE["reset"])
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to file '{path}'."
    except Exception as e:
        return f"Error: Cannot write to file '{path}'. {e}"

def list_files() -> str:
    try:
        items = sorted(os.listdir('.'))
        files = [f"[F] {item}" for item in items if os.path.isfile(item)]
        dirs = [f"[D] {item}/" for item in items if os.path.isdir(item)]
        if not files and not dirs:
            return "Current directory is empty."
        output = ""
        if dirs:
            output += "Directories:\n" + "\n".join(dirs)
        if files:
            if output:
                output += "\n\n"
            output += "Files:\n" + "\n".join(files)
        return output
    except Exception as e:
        return f"Error listing files: {e}"

def clear_screen() -> str:
    os.system('clear' if os.name == 'posix' else 'cls')
    return "Screen cleared."

def call_function(func_call, auto_save: bool):
    function_name = func_call.name
    function_args = getattr(func_call, 'args', {})
    
    if function_name == "run_command":
        return run_command(function_args.get("command", ""), auto_save)
    if function_name == "scan_subdomains":
        return scan_subdomains(function_args.get("domain", ""), auto_save)
    if function_name == "scan_ports":
        return scan_ports(function_args.get("target", ""), auto_save)
    if function_name == "enum_web":
        return enum_web(function_args.get("url", ""), auto_save)
    if function_name == "read_file":
        return read_file(function_args.get("path", ""))
    if function_name == "write_file":
        return write_file(function_args.get("path", ""), function_args.get("content", ""), auto_save)
    if function_name == "list_files":
        return list_files()
    if function_name == "clear_screen":
        return clear_screen()
    return f"Error: Function '{function_name}' not recognized."

def get_responsive_width():
    """Get responsive width for chat bubbles based on terminal size"""
    try:
        terminal_width = os.get_terminal_size().columns
        bubble_width = int(terminal_width * 0.8)
        bubble_width = min(bubble_width, 120)
        bubble_width = max(bubble_width, 60)
        return bubble_width
    except OSError:
        return 80

def parse_and_execute_tool_from_text(text: str, auto_save: bool = False):
    """
    Parse text output from AI and execute appropriate tools if detected.
    This function looks for command patterns in the AI's text response
    and executes the corresponding tools directly.
    """
    import re

    subfinder_match = re.search(r'(?:subfinder\s+-d\s+|--domain\s+)([^\s\]\n]+)', text, re.IGNORECASE)
    if subfinder_match:
        domain = subfinder_match.group(1).strip('"`\'')
        print(PALETTE["tool_call"] + f"\n[TOOL DETECTED] scan_subdomains({domain})" + PALETTE["reset"])
        result = scan_subdomains(domain, auto_save)
        print(PALETTE["tool_output"] + f"\n[TOOL OUTPUT]\n{result}" + PALETTE["reset"])
        return result

    nmap_patterns = [
        r'nmap\s+([^\n]+?)\s+(-p-|-p\s+\d+|\s)--target\s+([^\s\n]+)',
        r'nmap\s+([^\n]+?)\s+([^\s\n]+)',
        r'nmap\s+([^\s\n]+)'
    ]

    for pattern in nmap_patterns:
        nmap_matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in nmap_matches:
            cmd_parts = match.group(0).split()
            target = None
            for part in reversed(cmd_parts):
                if not part.startswith('-') and part.lower() != 'nmap':
                    target = part.strip('"`\'')
                    break
            if target:
                print(PALETTE["tool_call"] + f"\n[TOOL DETECTED] scan_ports({target})" + PALETTE["reset"])
                result = scan_ports(target, auto_save)
                print(PALETTE["tool_output"] + f"\n[TOOL OUTPUT]\n{result}" + PALETTE["reset"])
                return result

    gobuster_match = re.search(r'gobuster\s+dir\s+-u\s+([^\s\n]+)', text, re.IGNORECASE)
    if gobuster_match:
        url = gobuster_match.group(1).strip('"`\'')
        print(PALETTE["tool_call"] + f"\n[TOOL DETECTED] enum_web({url})" + PALETTE["reset"])
        result = enum_web(url, auto_save)
        print(PALETTE["tool_output"] + f"\n[TOOL OUTPUT]\n{result}" + PALETTE["reset"])
        return result

    read_file_match = re.search(r'(?:read_file|cat|less|more|head|tail)\s+([^\s\n]+)', text, re.IGNORECASE)
    if read_file_match:
        file_path = read_file_match.group(1).strip('"`\'')
        print(PALETTE["tool_call"] + f"\n[TOOL DETECTED] read_file({file_path})" + PALETTE["reset"])
        result = read_file(file_path)
        print(PALETTE["tool_output"] + f"\n[TOOL OUTPUT]\n{result}" + PALETTE["reset"])
        return result

    command_lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in command_lines:
        if line.startswith('$ ') or line.startswith('```') or any(cmd in line for cmd in ['sudo ', 'python ', 'curl ', 'wget ', 'ls ', 'pwd ', 'ps ', 'netstat ', 'whois ']):
            if line.startswith('$ '):
                command = line[2:].strip()
            elif line.startswith('```'):
                command = line[3:].strip() if len(line) > 3 else ''
                if command.endswith('```'):
                    command = command[:-3].strip()
            else:
                command = line.strip()

            command = command.strip('`')

            if command and not command.startswith('#'):
                print(PALETTE["tool_call"] + f"\n[TOOL DETECTED] run_command({command})" + PALETTE["reset"])
                result = run_command(command, auto_save)
                print(PALETTE["tool_output"] + f"\n[TOOL OUTPUT]\n{result}" + PALETTE["reset"])
                return result

    return None

def format_chat_bubble(content: str, sender: str = "AI", width: int = None, color: str = None) -> str:
    if width is None:
        width = get_responsive_width()

    lines = content.split('\n')
    formatted_lines = []

    content_color = Fore.WHITE + Style.NORMAL

    border_color = PALETTE["accent"]

    formatted_lines.append(border_color + "┌" + "─" * (width - 2) + "┐" + PALETTE["reset"])

    if sender:
        sender_prefix = f"┌─ {sender} "
        remaining_width = width - len(sender_prefix) - 1
        if remaining_width > 0:
            sender_line = sender_prefix + "─" * remaining_width + "┐"
            formatted_lines[0] = border_color + sender_line + PALETTE["reset"]

    import textwrap
    for line in lines:
        if line.strip() == "":
            formatted_lines.append(border_color + "│" + " " * (width - 2) + "│" + PALETTE["reset"])
        else:
            clean_line = line
            if clean_line.startswith('#') or clean_line.startswith('---'):
                if clean_line.startswith('---'):
                    continue
                else:
                    clean_line = clean_line.lstrip('# ')

            text_width = width - 4
            wrapped = textwrap.fill(clean_line, text_width, break_long_words=True, break_on_hyphens=True)
            for wrapped_line in wrapped.split('\n'):
                padded_line = wrapped_line.ljust(text_width)
                formatted_lines.append(f"{border_color}│{PALETTE['reset']} {content_color}{padded_line}{PALETTE['reset']} {border_color}│{PALETTE['reset']}")

    formatted_lines.append(border_color + "└" + "─" * (width - 2) + "┘" + PALETTE["reset"])

    bubble_str = "\n".join(formatted_lines)
    return "\n" + bubble_str

def render_markdown(text: str) -> str:
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        if line.strip() == '---' or line.strip().startswith('--- '):
            continue
        elif line.strip().startswith('# ') or line.strip().startswith('## ') or line.strip().startswith('### '):
            clean_line = line.lstrip('# ')
            processed_lines.append(clean_line)
        elif line.strip().startswith('#') and not line.strip().startswith('# '):
            processed_lines.append(line)
        else:
            processed_lines.append(line)

    text = '\n'.join(processed_lines)

    text = re.sub(r'^\*\s+(.+)', PALETTE["accent"] + '- ' + r'\1' + PALETTE["reset"], text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', lambda match: PALETTE["accent"] + Style.BRIGHT + match.group(1) + PALETTE["reset"], text)
    text = re.sub(r'\*(.*?)\*', lambda match: PALETTE["accent"] + match.group(1) + PALETTE["reset"], text)
    return text

def show_loading_indicator(stop_event):
    animation = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
    idx = 0
    while not stop_event.is_set():
        print(f"\r{PALETTE['accent']}{animation[idx % len(animation)]} Thinking...{PALETTE['reset']}", end="", flush=True)
        idx += 1
        time.sleep(0.1)
    print("\r" + " " * 30 + "\r", end="", flush=True)


def chat_loop(ai_type, API_KEY, MODEL, auto_save: bool, prompt_type: str = None):

    if prompt_type == "ctf":
        system_prompt = """
You are Strix, a Capture The Flag (CTF) competition assistant.

Rules:
1. Help users solve CTF challenges ethically and educationally.
2. Break down complex problems into understandable steps.
3. Explain methodologies and reasoning clearly.
4. Suggest multiple approaches when applicable.
5. Point out common pitfalls and how to avoid them.
6. Encourage learning and understanding over quick solutions.
7. Respect challenge categories (crypto, forensics, web, etc.).
8. USE TOOLS DIRECTLY when appropriate to assist with CTF challenges (e.g., run_command, read_file, write_file). Do not just describe the command in text - call the tool directly.
9. If you need to analyze a file, use read_file directly. If you need to run a command, use run_command directly.
10. Do not suggest commands for the user to run - instead, execute them yourself using tools when appropriate.
11. Do not use markdown heading formats (###, ##, #, ---) in your responses. Use regular text formatting instead.
12. Use • instead of * for lists.
        """
    elif prompt_type == "vuln-research":
        system_prompt = """
You are Strix, a vulnerability research assistant.

Rules:
1. Assist with vulnerability analysis and research methodologies.
2. NEVER exploit vulnerabilities in real systems without authorization.
3. Explain vulnerability concepts with practical examples.
4. Guide users through secure coding practices.
5. Help with CVE analysis and PoC development in controlled environments.
6. Provide guidance on responsible disclosure procedures.
7. Detail attack vectors and mitigation strategies.
8. Emphasize ethical considerations in all recommendations.
9. USE TOOLS DIRECTLY when appropriate to assist with vulnerability analysis (e.g., scan_subdomains, scan_ports, enum_web, run_command). Do not just describe the scan in text - call the tool directly.
10. If you need to enumerate subdomains, use scan_subdomains directly. If you need to scan ports, use scan_ports directly.
11. Do not suggest commands for the user to run - instead, execute them yourself using tools when appropriate.
12. Do not use markdown heading formats (###, ##, #, ---) in your responses. Use regular text formatting instead.
13. Use • instead of * for lists.
        """
    else:
        system_prompt = """
You are Strix, a technical penetration testing assistant.

Rules:
1. NEVER save scan results to a file automatically.
2. ONLY save to a file if the user explicitly asks (e.g., "save to file.txt" or "write this to output.txt").
3. When scanning (subdomains, ports, web), show output in the terminal only.
4. If the user provides a list and says "save to X", use 'write_file' with that content.
5. Be precise, technical, and do not hallucinate actions.
6. Match the user's language.
7. Use markdown: **bold**, *italic*, * lists.
8. You can create any script according to user requests, and can save the script via the save file function.
9. USE TOOLS DIRECTLY when appropriate (e.g., scan_subdomains, scan_ports, enum_web, run_command, read_file, write_file). Do not just describe the command in text - call the tool directly.
10. If you need to enumerate subdomains, use scan_subdomains directly. If you need to scan ports, use scan_ports directly.
11. Do not suggest commands for the user to run - instead, execute them yourself using tools when appropriate.
12. Do not use markdown heading formats (###, ##, #, ---) in your responses. Use regular text formatting instead.
13. Use • instead of * for lists.
        """


    if ai_type == "gemini":
        try:
            pentest_tool = define_tools()
            model = genai.GenerativeModel(model_name=MODEL, tools=[pentest_tool], system_instruction=system_prompt)
            chat = model.start_chat(history=[])
        except Exception as e:
            print(PALETTE["error"] + f"\n[ERROR] Failed to initialize Gemini model: {e}" + PALETTE["reset"])
            return
    elif ai_type == "openai":
        try:
            import openai
            client = openai.OpenAI(api_key=API_KEY)
            chat_history = [
                {"role": "system", "content": system_prompt}
            ]
        except Exception as e:
            print(PALETTE["error"] + f"\n[ERROR] Failed to initialize OpenAI client: {e}" + PALETTE["reset"])
            return
    elif ai_type == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=API_KEY)
            chat_history = [
                {"role": "system", "content": system_prompt}
            ]
        except Exception as e:
            print(PALETTE["error"] + f"\n[ERROR] Failed to initialize Anthropic client: {e}" + PALETTE["reset"])
            return
    elif ai_type == "groq":
        try:
            import groq
            client = groq.Groq(api_key=API_KEY)
            chat_history = [
                {"role": "system", "content": system_prompt}
            ]
        except Exception as e:
            print(PALETTE["error"] + f"\n[ERROR] Failed to initialize Groq client: {e}" + PALETTE["reset"])
            return
    elif ai_type == "mistral":
        try:
            import mistralai
            from mistralai.client import MistralClient
            from mistralai.models.chat_completion import ChatMessage
            client = MistralClient(api_key=API_KEY)
            chat_history = [
                ChatMessage(role="system", content=system_prompt)
            ]
        except Exception as e:
            print(PALETTE["error"] + f"\n[ERROR] Failed to initialize Mistral client: {e}" + PALETTE["reset"])
            return

    mode_text = " (Auto-Save MODE ON)" if auto_save else ""
    banner_lines = [
        "                           d8,         ",
        "           d8P            `8P          ",
        "        d888888P                       ",
        " .d888b,  ?88'    88bd88b  88b?88,  88P",
        " ?8b,     88P     88P'  `  88P `?8bd8P'",
        "   `?8b   88b    d88      d88  d8P?8b, ",
        "`?888P'   `?8b  d88'     d88' d8P' `?8b"
    ]
    print(PALETTE["banner_bg"] + PALETTE["accent"])
    for line in banner_lines:
        print("  " + line)
    print(PALETTE["reset"])
    print(PALETTE["accent"] + f"\nStrix with {ai_type.upper()} ({MODEL}) model is ready{mode_text}!" + PALETTE["reset"])
    print(PALETTE["muted"] + "Type '!exit' or 'quit' to leave.\n" + PALETTE["reset"])

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.formatted_text import ANSI
    
        session = PromptSession(history=InMemoryHistory())
        use_prompt_toolkit = True
    except ImportError:
        print(PALETTE["error"] + "Warning: 'prompt_toolkit' not installed. Arrow keys and history disabled." + PALETTE["reset"])
        use_prompt_toolkit = False

    while True:
        try:
            if use_prompt_toolkit:
                placeholder_text = ANSI(PALETTE["placeholder"] + "Type your message or @path/to/file" + PALETTE["reset"])

                user_input = session.prompt(
                    "\n> ",
                    placeholder=placeholder_text
                )
            else:
                user_input = input("\n> ")

            if user_input.lower() in ['!exit', 'quit']:
                print(PALETTE["success"] + "Goodbye!" + PALETTE["reset"])
                break
            if not user_input.strip():
                continue

            if user_input.startswith('@'):
                file_path = user_input[1:].strip()
                if file_path:
                    file_content = read_file(file_path)
                    print(format_chat_bubble(file_content, f"File Content: {file_path}"))
                    continue
                else:
                    print(PALETTE["error"] + "Please provide a file path after @ (e.g., @strix/main.py)" + PALETTE["reset"])
                    continue

            stop_event = threading.Event()
            loader_thread = threading.Thread(target=show_loading_indicator, args=(stop_event,))
            loader_thread.daemon = True
            loader_thread.start()


            if ai_type == "gemini":
                try:
                    response = chat.send_message(user_input)
                except Exception as e:
                    stop_event.set()
                    loader_thread.join()
                    if "MALFORMED_FUNCTION_CALL" in str(e):
                        print(PALETTE["error"] + "\n[ERROR] Invalid tool call. Be explicit." + PALETTE["reset"])
                    else:
                        print(PALETTE["error"] + f"\n[ERROR] {e}" + PALETTE["reset"])
                    continue
                finally:
                    stop_event.set()
                    loader_thread.join()

                while True:
                    candidate = response.candidates[0]
                    finish_reason = candidate.finish_reason

                    if finish_reason == genai.protos.Candidate.FinishReason.MALFORMED_FUNCTION_CALL:
                        print(PALETTE["error"] + "\n[ERROR] Invalid function call." + PALETTE["reset"])
                        break

                    response_parts = candidate.content.parts
                    function_call = None
                    for part in response_parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_call = part.function_call
                            break

                    if function_call:
                        user_request_lower = user_input.lower()
                        is_text_request = any(keyword in user_request_lower for keyword in
                                            ['strategi', 'strategy', 'how to', 'explain', 'how can i', 'tips',
                                             'advice', 'tutorial', 'guide', 'write', 'buatkan', 'buat',
                                             'what is', 'describe', 'buatkan strategi', 'cara', 'step by step'])

                        if is_text_request and function_call.name in ['run_command', 'scan_subdomains', 'scan_ports', 'enum_web']:
                            stop_event.set()
                            loader_thread.join()

                            try:
                                guidance_text = f"Please provide the requested information in text format instead of suggesting commands. User requested: {user_input}"

                                stop_event = threading.Event()
                                loader_thread = threading.Thread(target=show_loading_indicator, args=(stop_event,))
                                loader_thread.daemon = True
                                loader_thread.start()

                                response = chat.send_message(guidance_text)
                            except Exception as guidance_err:
                                stop_event.set()
                                loader_thread.join()
                                print(PALETTE["error"] + f"\n[GUIDANCE ERROR] {guidance_err}" + PALETTE["reset"])
                                break
                            continue

                        try:
                            function_response = call_function(function_call, auto_save)
                            print(PALETTE["command"] + f"\n[OUTPUT]\n{function_response}" + PALETTE["reset"])

                            stop_event = threading.Event()
                            loader_thread = threading.Thread(target=show_loading_indicator, args=(stop_event,))
                            loader_thread.daemon = True
                            loader_thread.start()
                            try:
                                response = chat.send_message(
                                    genai.protos.FunctionResponse(
                                        name=function_call.name,
                                        response={"result": function_response}
                                    )
                                )
                            finally:
                                stop_event.set()
                                loader_thread.join()
                        except Exception as call_err:
                            print(PALETTE["error"] + f"\n[FUNCTION ERROR] {call_err}" + PALETTE["reset"])
                            break
                    else:
                        final_text = "".join([part.text for part in response_parts if hasattr(part, 'text')])
                        if final_text.strip():
                            rendered_text = render_markdown(final_text)
                            print(format_chat_bubble(rendered_text, "Strix"))
                        break
            else:
                if ai_type == "openai":
                    try:
                        chat_history.append({"role": "user", "content": user_input})
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=chat_history,
                            temperature=0.7,
                            max_tokens=2048
                        )
                        ai_response = response.choices[0].message.content
                        chat_history.append({"role": "assistant", "content": ai_response})

                        tool_result = parse_and_execute_tool_from_text(ai_response, auto_save)
                        if tool_result is None:
                            print(format_chat_bubble(ai_response, "Strix"))

                    except Exception as e:
                        stop_event.set()
                        loader_thread.join()
                        print(PALETTE["error"] + f"\n[ERROR] {e}" + PALETTE["reset"])
                        continue
                    finally:
                        stop_event.set()
                        loader_thread.join()
                        
                elif ai_type == "anthropic":
                    try:
                        chat_history.append({"role": "user", "content": user_input})
                        response = client.messages.create(
                            model=MODEL,
                            messages=chat_history[1:],
                            max_tokens=2048,
                            temperature=0.7
                        )
                        ai_response = response.content[0].text
                        chat_history.append({"role": "assistant", "content": ai_response})

                        tool_result = parse_and_execute_tool_from_text(ai_response, auto_save)
                        if tool_result is None:
                            print(format_chat_bubble(ai_response, "Strix"))

                    except Exception as e:
                        stop_event.set()
                        loader_thread.join()
                        print(PALETTE["error"] + f"\n[ERROR] {e}" + PALETTE["reset"])
                        continue
                    finally:
                        stop_event.set()
                        loader_thread.join()
                        
                elif ai_type == "groq":
                    try:
                        chat_history.append({"role": "user", "content": user_input})
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=chat_history,
                            temperature=0.7,
                            max_tokens=2048
                        )
                        ai_response = response.choices[0].message.content
                        chat_history.append({"role": "assistant", "content": ai_response})

                        tool_result = parse_and_execute_tool_from_text(ai_response, auto_save)
                        if tool_result is None:
                            print(format_chat_bubble(ai_response, "Strix"))

                    except Exception as e:
                        stop_event.set()
                        loader_thread.join()
                        print(PALETTE["error"] + f"\n[ERROR] {e}" + PALETTE["reset"])
                        continue
                    finally:
                        stop_event.set()
                        loader_thread.join()
                        
                elif ai_type == "mistral":
                    try:
                        chat_history.append(ChatMessage(role="user", content=user_input))
                        response = client.chat(
                            model=MODEL,
                            messages=chat_history,
                            temperature=0.7,
                            max_tokens=2048
                        )
                        ai_response = response.choices[0].message.content
                        chat_history.append(ChatMessage(role="assistant", content=ai_response))

                        tool_result = parse_and_execute_tool_from_text(ai_response, auto_save)
                        if tool_result is None:
                            print(format_chat_bubble(ai_response, "Strix"))

                    except Exception as e:
                        stop_event.set()
                        loader_thread.join()
                        print(PALETTE["error"] + f"\n[ERROR] {e}" + PALETTE["reset"])
                        continue
                    finally:
                        stop_event.set()
                        loader_thread.join()

        except KeyboardInterrupt:
            print("\n" + PALETTE["muted"] + "Exiting program." + PALETTE["reset"])
            break
        except Exception as e:
            print(PALETTE["error"] + f"\n[UNEXPECTED ERROR] {e}" + PALETTE["reset"])
            continue

def main():
    parser = argparse.ArgumentParser(description="Strix: Command-line pentesting assistant.")
    parser.add_argument('--auto-save', action='store_true', help='Bypass confirmation prompts (USE WITH CAUTION)')
    parser.add_argument('--prompt', choices=['pentest', 'ctf', 'vuln-research'], 
                       help='Select system prompt: pentest (default), ctf, vuln-research')
    

    args = parser.parse_args()
    

    ai_type, API_KEY, MODEL = initialize_ai()
    chat_loop(ai_type, API_KEY, MODEL, auto_save=args.auto_save, prompt_type=args.prompt)


if __name__ == "__main__":
    main()  
