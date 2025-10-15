from src.code_generator import generate_code
from src.file_handler import handle_files, install_extension
from src.constants import OUTPUT_DIRECTORY

def main():
    user_prompt = input("Enter your prompt: ")
    from rich import print as rprint
    rprint("[blue]🤖 Generating code...[/blue]")
    response = generate_code(user_prompt, debug_mode=False)
    handle_files(response)
    install_extension(f"{OUTPUT_DIRECTORY}/{response.appName.replace(' ', '_').lower()}")

if __name__ == "__main__":
    main()
