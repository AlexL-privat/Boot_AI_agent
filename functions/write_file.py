import os

def write_file(working_directory, file_path, content):
    """
    Writes content to a file safely within a permitted working directory.

    Parameters:
        working_directory (str): The base directory allowed for writing.
        file_path (str): Relative or absolute path to the file to write.
        content (str): Text content to write into the file.

    Returns:
        str: Success or error message.
    """
    try:
        # Build the full path
        full_path = os.path.abspath(os.path.join(working_directory, file_path))
        working_directory = os.path.abspath(working_directory)

        # Security check: Ensure full_path is inside working_directory
        if not full_path.startswith(working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        # Ensure parent directories exist
        parent_dir = os.path.dirname(full_path)
        os.makedirs(parent_dir, exist_ok=True)

        # Write content to the file (overwriting if it exists)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        # Catch any other unexpected errors
        return f'Error: {e}'