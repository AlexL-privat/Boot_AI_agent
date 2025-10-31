import os
from google.genai import types
from config import *

def get_file_content(working_directory, file_path):
    """
    Return content of a file as string.

    Parameters:
        working_directory (str): Base directory (root of allowed operations)
        file_path (str): Relative path inside working_directory

    Returns:
        a str: File content up to the character limit, or an error message string.
    """
    try:
        # Build the full path
        full_path = os.path.abspath(os.path.join(working_directory, file_path))
        working_directory = os.path.abspath(working_directory)

        # Security check: Ensure full_path is inside working_directory
        if not full_path.startswith(working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Ensure the path exists and is a directory
        if not os.path.isfile(full_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        # Open and read the file    
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Truncate if longer than character limit
        if len(content) > FILE_CHARACTER_LIMIT:
            truncated_content = content[:FILE_CHARACTER_LIMIT]
            truncated_content += f'\n[...File "{full_path}" truncated at 10000 characters]'
            return truncated_content

        return content

    except Exception as e:
        # Catch any other unexpected errors
        return f'Error: {e}'

    
# Define the function schema for AI integration
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns content of a file as string up to a preconfigured character limit, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose content is returned, relative to the working directory. If path is invalid or the file is to accessible an error is returned.",
            ),
        },
    ),
)