import sys
from google.genai import types

# Import the actual function implementations
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file


#helper function to handle functions calls
def call_function(function_call_part, verbose=False):
    """
    Executes a function call returned by Gemini and returns a structured Content response.

    Args:
        function_call_part (types.FunctionCall): The function call object from Gemini.
        verbose (bool): Whether to print detailed information.

    Returns:
        types.Content: A tool response indicating success or error.
    """
    function_name = function_call_part.name
    function_args = dict(function_call_part.args or {})

    # Always enforce working directory (not controlled by the LLM)
    function_args["working_directory"] = "./calculator"

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    # Map function names to actual functions
    function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
    }

    # If invalid function name
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # Try to call the actual function
    try:
        function_result = function_map[function_name](**function_args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
    
    except Exception as e:
    # Handle unexpected errors gracefully
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Error calling {function_name}: {str(e)}"},
                )
            ],
        )