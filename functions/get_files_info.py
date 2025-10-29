import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    """
    Lists file info for a directory inside the working_directory.

    Parameters:
        working_directory (str): Base directory (root of allowed operations)
        directory (str): Relative path inside working_directory

    Returns:
        list[dict] | str: A list of file info dicts, or an error message string.
    """
    try:
    # Build the full path
        full_path = os.path.abspath(os.path.join(working_directory, directory))
        working_directory = os.path.abspath(working_directory)

    # Security check: Ensure full_path is inside working_directory
        if not full_path.startswith(working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    # Ensure the path exists and is a directory
        if not os.path.isdir(full_path):
            return f'Error: "{directory}" is not a directory'

    # Gather file info
        lines = []
        for entry in os.listdir(full_path):
            entry_path = os.path.join(full_path, entry)
            try:
                is_dir = os.path.isdir(entry_path)
                size = os.path.getsize(entry_path)
                lines.append(f"- {entry}: file_size={size} bytes, is_dir={is_dir}")
            except Exception as e:
                # Catch errors per entry (e.g., permission denied)
                return f"Error: Could not access '{entry}': {e}"

        return "\n".join(lines)

    except Exception as e:
    # Catch all higher-level errors (e.g., invalid path)
        return f"Error: {e}"


# Define the function schema for AI integration
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)