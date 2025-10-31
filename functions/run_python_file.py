import os
import subprocess
import sys
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    """
    Executes a Python file safely within a working directory.

    Parameters:
        working_directory (str): Base directory for allowed execution.
        file_path (str): Relative path to the Python file to execute.
        args (list): Additional command-line arguments to pass to the script.

    Returns:
        str: Formatted output, or an error message prefixed with "Error:".
    """
    try:
        # Resolve absolute paths
        full_path = os.path.abspath(os.path.join(working_directory, file_path))
        working_directory = os.path.abspath(working_directory)

        # Security check: ensure file is inside working_directory
        if not full_path.startswith(working_directory):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Check file existence
        if not os.path.isfile(full_path):
            return f'Error: File "{file_path}" not found.'

        # Check file extension
        if not full_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'

        # Build the command: python <file> [args...]
        cmd = [sys.executable, full_path] + args

        # Run the subprocess
        completed_process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=30
        )

        stdout = completed_process.stdout.strip()
        stderr = completed_process.stderr.strip()
        exit_code = completed_process.returncode

        # Prepare output
        output_lines = []
        if stdout:
            output_lines.append(f"STDOUT:\n{stdout}")
        if stderr:
            output_lines.append(f"STDERR:\n{stderr}")
        if exit_code != 0:
            output_lines.append(f"Process exited with code {exit_code}")

        if not output_lines:
            return "No output produced."

        return "\n".join(output_lines)

    except Exception as e:
        return f"Error: executing Python file: {e}"
    

# Define the function schema for AI integration
schema_run_python_file = types.FunctionDeclaration(
    name="get_file_content",
    description="Executes a python file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the python file that is executed, relative to the working directory. If path is invalid or it's not a python fiel an error is returned.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="A list of command-line arguments to pass to the python script.",
            ),
        },
    ),
)