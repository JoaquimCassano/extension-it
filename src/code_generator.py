import openai
from pydantic import BaseModel
from rich import print as rprint
from src.constants import CODE_GENERATION_PROMPT_TEMPLATE, VICINAE_INSTRUCTIONS

class File(BaseModel):
    path: str
    content: str

class ResponseFormat(BaseModel):
    files: list[File]
    notes: str
    configurationNeeded: bool
    appName: str

client = openai.OpenAI()

def generate_code(prompt, debug_mode: bool = False):
    rprint(f"[blue]🤖 Generating code for prompt: {prompt}[/blue]")
    instructions = CODE_GENERATION_PROMPT_TEMPLATE.format(instructions=VICINAE_INSTRUCTIONS)
    response = client.responses.parse(
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
    if debug_mode:
        rprint(f"[cyan]Debug: Response parsed successfully[/cyan]")
        rprint(f"[cyan]App Name: {response.output_parsed.appName}[/cyan]")
        rprint(f"[cyan]Files generated: {len(response.output_parsed.files)}[/cyan]")
    print("\n \n \n \n")
    print(response)
    return response.output_parsed
