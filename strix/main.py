
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


PALETTE = {
    "accent": Fore.CYAN + Style.BRIGHT,
    "muted": Fore.WHITE + Style.DIM,
    "success": Fore.GREEN + Style.BRIGHT,
    "error": Fore.RED + Style.BRIGHT,
    "command": Fore.YELLOW + Style.NORMAL,
    "banner_bg": Back.MAGENTA,
    "reset": Style.RESET_ALL
}


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


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
            "2": ("openai", os.getenv("OPENAI_API_KEY"), "gpt-4"),
            "3": ("anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-sonnet"),
            "4": ("groq", os.getenv("GROQ_API_KEY"), "llama3-70b-8192"),
            "5": ("mistral", os.getenv("MISTRAL_API_KEY"), "mistral-small-latest"),
        }
        
        if model_choice in model_map:
            return model_map[model_choice]
        else:
            return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.5-flash"
    
    print(PALETTE["accent"] + "\nSelect AI Model:" + PALETTE["reset"])
    print("1. Google Gemini (gemini-2.5-flash)")
    print("2. OpenAI GPT-4 (gpt-4)")
    print("3. Anthropic Claude (claude-3-sonnet)")
    print("4. Groq LLaMA 3 (llama3-70b-8192)")
    print("5. Mistral (mistral-small-latest)")
    
    choice = input("Enter choice (1-5) [default: 1]: ").strip()
    

    with open(env_path, 'a') as f:
        f.write(f"\nSTRIX_MODEL_CHOICE={choice}\n")
    
    if choice == "2":
        return "openai", os.getenv("OPENAI_API_KEY"), "gpt-4"
    elif choice == "3":
        return "anthropic", os.getenv("ANTHROPIC_API_KEY"), "claude-3-sonnet"
    elif choice == "4":
        return "groq", os.getenv("GROQ_API_KEY"), "llama3-70b-8192"
    elif choice == "5":
        return "mistral", os.getenv("MISTRAL_API_KEY"), "mistral-small-latest"
    else:
        return "gemini", os.getenv("GOOGLE_API_KEY"), "gemini-2.5-flash"

def validate_api_key(ai_type, api_key):
    if not api_key or api_key.strip() == "":
        print(PALETTE["error"] + f"\nError: {ai_type.upper()}_API_KEY not found in .env file." + PALETTE["reset"])
        print(PALETTE["muted"] + f"Please add your {ai_type} API key to ~/Strix/.env file." + PALETTE["reset"])
        print(PALETTE["muted"] + "Example: " + ai_type.upper() + "_API_KEY=your_api_key_here" + PALETTE["reset"])
        

        setup_choice = input(PALETTE["accent"] + "\nWould you like to add your API key now? (y/N): " + PALETTE["reset"]).strip().lower()
        
        if setup_choice == 'y':
            api_key_value = input(f"Enter your {ai_type} API key: ").strip()
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
    """Initialize AI model after model selection"""
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
    if not auto_save:
        print(PALETTE["command"] + "\n[AI PROPOSED COMMAND]\n  $ " + command + "\n" + ("-" * 40) + PALETTE["reset"])
        confirmation = input("Are you sure you want to execute this command? [y/N]: ").strip().lower()
        if confirmation != 'y':
            return "Command cancelled by user."
    else:
        print(PALETTE["muted"] + f"\n[AUTO-SAVE MODE ON] Executing: $ {command}" + PALETTE["reset"])
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True, encoding='utf-8')
        stdout, stderr = result.stdout or "", result.stderr or ""
        combined = stdout + ("\n[STDERR]\n" + stderr if stderr else "")
        return combined.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: Command failed. Exit code {e.returncode}.\nStderr: {e.stderr}"
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
        print(PALETTE["command"] + f"\n[AI PROPOSED WRITE]\n  Path: {path}\n  Content preview:\n---\n{content_preview}\n---" + PALETTE["reset"])
        confirmation = input("Are you sure you want to write this file? [y/N]: ").strip().lower()
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

def render_markdown(text: str) -> str:
    text = re.sub(r'^\*\s+(.+)', PALETTE["accent"] + '- ' + r'\1' + PALETTE["reset"], text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', lambda match: PALETTE["accent"] + Style.BRIGHT + match.group(1) + PALETTE["reset"], text)
    text = re.sub(r'\*(.*?)\*', lambda match: PALETTE["accent"] + match.group(1) + PALETTE["reset"], text)
    return text

def show_loading_indicator(stop_event):
    animation = ["|", "/", "-", "\\"]
    idx = 0
    while not stop_event.is_set():
        print(f"\r{PALETTE['muted']}Thinking... {animation[idx % len(animation)]}{PALETTE['reset']}", end="", flush=True)
        idx += 1
        time.sleep(0.1)
    print("\r" + " " * 20 + "\r", end="", flush=True)


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
        """
    

    if ai_type == "gemini":
        pentest_tool = define_tools()
        model = genai.GenerativeModel(model_name=MODEL, tools=[pentest_tool], system_instruction=system_prompt)
        chat = model.start_chat(history=[])
    elif ai_type == "openai":


        pass
    elif ai_type == "anthropic":

        pass
    elif ai_type == "groq":


        pass
    elif ai_type == "mistral":


        pass

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
        session = PromptSession(history=InMemoryHistory())
        use_prompt_toolkit = True
    except ImportError:
        print(PALETTE["error"] + "Warning: 'prompt_toolkit' not installed. Arrow keys and history disabled." + PALETTE["reset"])
        use_prompt_toolkit = False

    while True:
        try:
            if use_prompt_toolkit:
                user_input = session.prompt("\nStrix > ")
            else:
                user_input = input("\nStrix > ")

            if user_input.lower() in ['!exit', 'quit']:
                print(PALETTE["success"] + "Goodbye!" + PALETTE["reset"])
                break
            if not user_input.strip():
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
                        try:
                            print(PALETTE["muted"] + f"\n[AI THOUGHT]\nCalling function '{function_call.name}'" + PALETTE["reset"])
                            function_response = call_function(function_call, auto_save)
                            print(PALETTE["command"] + f"\n[TOOL OUTPUT]\n{function_response}" + PALETTE["reset"])

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
                            print(PALETTE["accent"] + f"\n[AI ANSWER]\n{rendered_text}" + PALETTE["reset"])
                        break
            else:


                print(PALETTE["error"] + f"\nFunction calling with tools is not yet implemented for {ai_type.upper()}. Using basic chat mode..." + PALETTE["reset"])

                print(PALETTE["muted"] + f"\n[{ai_type.upper()}] Response would appear here..." + PALETTE["reset"])
                print(PALETTE["muted"] + "Function calling with tools is currently only supported with Gemini models." + PALETTE["reset"])

        except KeyboardInterrupt:
            print("\n" + PALETTE["muted"] + "Exiting program." + PALETTE["reset"])
            break
        except Exception as e:
            print(PALETTE["error"] + f"\n[UNEXPECTED ERROR] {e}" + PALETTE["reset"])
            continue

def main():
    """Main entry point for the strix command."""
    parser = argparse.ArgumentParser(description="Strix: Command-line pentesting assistant.")
    parser.add_argument('--auto-save', action='store_true', help='Bypass confirmation prompts (USE WITH CAUTION)')
    parser.add_argument('--prompt', choices=['pentest', 'ctf', 'vuln-research'], 
                       help='Select system prompt: pentest (default), ctf, vuln-research')
    

    args = parser.parse_args()
    

    ai_type, API_KEY, MODEL = initialize_ai()
    chat_loop(ai_type, API_KEY, MODEL, auto_save=args.auto_save, prompt_type=args.prompt)


if __name__ == "__main__":
    main()