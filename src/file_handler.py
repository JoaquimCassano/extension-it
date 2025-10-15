import os
import subprocess
from rich import print as rprint
from rich.prompt import Prompt
from src.constants import PLACEHOLDER_IMAGE_PATH, OUTPUT_DIRECTORY, DEFAULT_PACKAGE_MANAGER, PACKAGE_MANAGERS

def install_extension(app_name: str):
    choice = Prompt.ask(f"Do you want to install the extension '{app_name}' now? (y/n)", choices=["y", "n"], default="y")
    if choice == "y":
        rprint(f"[blue]🔄 Installing extension '{app_name}'...[/blue]")
        try:
            package_manager = Prompt.ask("Which package manager do you use?", choices=PACKAGE_MANAGERS, default=DEFAULT_PACKAGE_MANAGER)
            match package_manager:
                case "npm":
                    subprocess.run(["npx", "vici", "build"], check=True, cwd=app_name)
                case "yarn":
                    subprocess.run(["yarn", "vici", "build"], check=True, cwd=app_name)
                case "pnpm":
                    subprocess.run(["pnpm", "vici", "build"], check=True, cwd=app_name)
            rprint(f"[green]✅ Extension '{app_name}' installed successfully![/green]")
        except subprocess.CalledProcessError as e:
            rprint(f"[red]❌ Failed to install extension '{app_name}'. Please install it manually.[/red]")
            rprint(f"[red]Error details: {e}[/red]")
    else:
        rprint(f"[yellow]⚠️ Skipped installation. You can install the extension '{app_name}' later.[/yellow]")


def handle_files(response):
    appName = f"{OUTPUT_DIRECTORY}/{response.appName.replace(' ', '_').lower()}"
    os.makedirs(appName, exist_ok=True)
    for file in response.files:
        file_path = os.path.join(appName, file.path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if file_path.split(".")[-1] in ["png"]:
            with open(PLACEHOLDER_IMAGE_PATH, 'rb') as f:
                with open(file_path, 'wb') as out:
                    out.write(f.read())
            continue
        with open(file_path, 'w') as f:
            f.write(file.content)
    rprint(f"[green]✅ Generated {len(response.files)} files in '{appName}' directory.[/green]")
    if response.configurationNeeded:
        rprint("[yellow]⚠️ WARNING: Some configuration is needed. Please check the notes for details.[/yellow]")
        rprint(f"[blue]📝 Notes:\n{response.notes}[/blue]")
        rprint(f"[green]✅ Extension '{response.appName}' generated with some configuration needed.[/green]")
    else:
        rprint(f"[green]✅ Extension '{response.appName}' generated successfully without additional configuration.[/green]")
