import openai, os
from rich import print as rprint
from rich.prompt import Prompt
from pydantic import BaseModel
import subprocess

class File(BaseModel):
  path: str
  content: str

class ResponseFormat(BaseModel):
  files: list[File]
  notes: str
  configurationNeeded: bool
  appName: str

client = openai.OpenAI()

def install_extension(app_name: str):
  choice = Prompt.ask(f"Do you want to install the extension '{app_name}' now? (y/n)", choices=["y", "n"], default="y")
  if choice == "y":
    rprint(f"[blue]🔄 Installing extension '{app_name}'...[/blue]")
    try:
      package_manager = Prompt.ask("Which package manager do you use?", choices=["npm", "yarn", "pnpm"], default="npm")
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



def handle_files(response:ResponseFormat):
  appName = f"output/{response.appName.replace(" ", "_").lower()}"
  os.makedirs(appName, exist_ok=True)
  for file in response.files:
    file_path = os.path.join(appName, file.path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if file_path.split(".")[-1] in ["png"]:
      with open("assets/placeholder_image.png", 'rb') as f:
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

def generate_code(prompt, debug_mode:bool=False):
  rprint(f"[blue]🤖 Generating code for prompt: {prompt}[/blue]")
  instructions = f"""
  You are an expert software engineer. Your role is to generate a Vicinae (or raycast) extension based on the user's instruction. The extension should be functional and ready to use (beside some configuration of keys etc.). Ensure the UI and UX work seamlessly, and everything the user expects can be done. Follow these guidelines:
  Context:
  {open('instructions/vicinae-instructions.txt', 'r').read()}
  """
  response =  client.responses.parse(
    model="gpt-5-mini",
    input=[
      {
        "role": "user",
        "content": "Generate a Vicinae extension based on this description and instructions:\n" + prompt
      }
    ],
    reasoning={"effort": "low"},
    instructions=instructions,
    text_format=ResponseFormat,
  )
  if debug_mode == True:
      rprint(f"[cyan]Debug: Response parsed successfully[/cyan]")
      rprint(f"[cyan]App Name: {response.output_parsed.appName}[/cyan]")
      rprint(f"[cyan]Files generated: {len(response.output_parsed.files)}[/cyan]")
  print("\n \n \n \n")

  print(response)
  return response.output_parsed


if __name__ == "__main__":
  user_prompt = input("Enter your prompt: ")
  rprint("[blue]🤖 Generating code...[/blue]")
  response = generate_code(user_prompt, debug_mode=False)
  handle_files(response)
  install_extension(f"output/{response.appName.replace(' ', '_').lower()}")