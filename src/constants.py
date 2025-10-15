VICINAE_INSTRUCTIONS = open('instructions/vicinae-instructions.txt', 'r').read()

CODE_GENERATION_PROMPT_TEMPLATE = """You are an expert software engineer. Your role is to generate a Vicinae (or raycast) extension based on the user's instruction. The extension should be functional and ready to use (beside some configuration of keys etc.). Ensure the UI and UX work seamlessly, and everything the user expects can be done. Follow these guidelines:

Context:
{instructions}
"""

PLACEHOLDER_IMAGE_PATH = "assets/placeholder_image.png"
OUTPUT_DIRECTORY = "output"
DEBUG_MODE = False
DEFAULT_PACKAGE_MANAGER = "npm"
PACKAGE_MANAGERS = ["npm", "yarn", "pnpm"]
