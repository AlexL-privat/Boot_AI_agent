import os
from dotenv import load_dotenv
from google import genai
from google.genai import Client, types
import sys

# Load environment variables from file
load_dotenv("gemini.env")

# Get the API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in environment.")
    sys.exit(1)

# Initialize the Gemini client
client = genai.Client(api_key=api_key)



def main(argv):
    # Handle --verbose flag
    verbose = "--verbose" in argv
    argv = [arg for arg in argv if arg != "--verbose"]

    # If no arguments, print a message and exit with code 1
    if argv == []:
        print("Please provide a prompt as a command-line argument.")
        sys.exit(1)

    # Combine arguments into a single prompt
    user_prompt = " ".join(argv)

    #intialize token counters
    prompt_tokens = 0
    response_tokens = 0

    # Prepare the message structure for the API
    messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    # Generate a response using Gemini
    response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    )

    # Get token usage (if available)
    prompt_tokens += getattr(response.usage_metadata, "prompt_token_count", 0)
    response_tokens += getattr(response.usage_metadata, "candidates_token_count", 0)

    # If verbose, print debug information
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")

    # Print the generated response
    print(response.text)
    

if __name__ == "__main__":
    main(sys.argv[1:])
