import openai, os
from rich import print as rprint
from pydantic import BaseModel

class File(BaseModel):
  path: str
  content: str

class ResponseFormat(BaseModel):
  files: list[File]
  notes: str
  configurationNeeded: bool
  appName: str

client = openai.OpenAI()



def handle_files(response:ResponseFormat):
  os.makedirs(response.appName, exist_ok=True)
  for file in response.files:
    file_path = os.path.join(response.appName, file.path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if file_path.split(".")[-1] in ["png"]:
      with open("assets/placeholder_image.png", 'rb') as f:
        with open(file_path, 'wb') as out:
          out.write(f.read())
      continue
    with open(file_path, 'w') as f:
      f.write(file.content)
  rprint(f"[green]✅ Generated {len(response.files)} files in '{response.appName}' directory.[/green]")
  if response.configurationNeeded:
    rprint("[yellow]⚠️ WARNING: Some configuration is needed. Please check the notes for details.[/yellow]")
    rprint(f"[blue]📝 Notes:\n{response.notes}[/blue]")
    rprint(f"[green]✅ Extension '{response.appName}' generated with some configuration needed.[/green]")
  else:
    rprint(f"[green]✅ Extension '{response.appName}' generated successfully without additional configuration.[/green]")

def generate_code(prompt, debug_mode:bool=False):
  rprint(f"[blue]🤖 Generating code for prompt: {prompt}[/blue]")
  instructions = f"""
  You are an expert software engineer. Your role is to generate a Vicinae (or raycast) extension based on the user's instruction. The extension should be functional and ready to use (beside some configuration of keys etc.). If the extension needs an image, use the filename img.png and the content will be "placeholder". Follow these guidelines:
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
    reasoning={"effort": "minimal"},
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