VICINAE_INSTRUCTIONS = open('instructions/vicinae-instructions.txt', 'r').read()

CODE_GENERATION_PROMPT_TEMPLATE = """You are an expert software engineer. Your role is to generate a Vicinae (or raycast) extension based on the user's instruction. The extension should be functional and ready to use (beside some configuration of keys etc.). Ensure the UI and UX work seamlessly, and everything the user expects can be done. Polish the UI as much as possible, adding icons and visual elements for empty states etc. Follow these guidelines:

Context:
{instructions}

Additional instructions:
- The OAUTH integration does NOT work. Instead, create a authentication flow yourself using the settings and local storage. It doesn't need to be complex like PKCE.
- the AI features are also not available. instead, use Openai's sdk.
- consider the extension will be running in linux.
- remember to use localstorage whenever the app needs persistent data.
"""

PLACEHOLDER_IMAGE_PATH = "assets/placeholder_image.png"
OUTPUT_DIRECTORY = "output"
DEBUG_MODE = False
DEFAULT_PACKAGE_MANAGER = "npm"
PACKAGE_MANAGERS = ["npm", "yarn", "pnpm"]
