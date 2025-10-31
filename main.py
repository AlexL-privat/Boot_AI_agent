import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import Client, types
from config import *

# Import the function schema
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file

#Import helper function to call functions
from call_function import call_function

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


    # Define the available functions for the AI to use
    available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
    )

    # Intialize the conversation messages list
    messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    MAX_ITERATIONS = 20

    for iteration in range(MAX_ITERATIONS):
        try:
            #Call the model to generate content
            response = client.models.generate_content(
            model = model_name,
            contents = messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt
                )
            )

            # Get token usage (if available)
            usage = getattr(response, "usage_metadata", None)
            if usage:
                pt = getattr(usage, "prompt_token_count", 0) or 0
                ct = getattr(usage, "candidates_token_count", 0) or 0
                prompt_tokens += pt
                response_tokens += ct

            # If verbose, print debug information
            if verbose:
                print(f"User prompt: {user_prompt}")
                print(f"Prompt tokens: {prompt_tokens}")
                print(f"Response tokens: {response_tokens}")

            # Add each candidate’s content to the conversation
            if hasattr(response, "candidates"):
                for candidate in response.candidates:
                    if hasattr(candidate, "content") and candidate.content:
                        messages.append(candidate.content)  # Add model’s reply

                        # Check for function calls inside this candidate
                        for part in candidate.content.parts:
                            if hasattr(part, "function_call") and part.function_call:
                                # Call the actual Python function
                                function_call_result = call_function(part.function_call, verbose=verbose)

                                # Validate result structure
                                try:
                                    response_data = function_call_result.parts[0].function_response.response
                                except (AttributeError, IndexError) as e:
                                    raise RuntimeError(
                                        f"❌ Fatal: call_function() did not return a valid response structure: {e}"
                                    )

                                # Print function call result if verbose
                                if verbose:
                                    print(f"-> {response_data}")

                                # Convert the function response into a user message
                                function_response_message = types.Content(
                                    role="user",
                                    parts=function_call_result.parts,
                                )

                                # Add it to the ongoing conversation
                                messages.append(function_response_message)

            done_texts = []
            for cand in getattr(response, "candidates", []):
                content = getattr(cand, "content", None)
                if not content: continue
                has_call = any(getattr(p, "function_call", None) for p in content.parts)
                if not has_call:
                    for p in content.parts:
                        if getattr(p, "text", None):
                            done_texts.append(p.text)
            if done_texts:
                print("Final response:")
                print("\n".join(done_texts))
                break

        except Exception as e:
            print(f"❌ Error during iteration {iteration + 1}: {e}")
            break
    else:
        print("⚠️ Max iterations reached without final response.")


    # If the model didn’t call a function, print fallback text
    if not hasattr(response, "candidates") or not response.candidates:
        print(getattr(response, "text", None) or "⚠️ No text content found in response.")


if __name__ == "__main__":
    main(sys.argv[1:])
