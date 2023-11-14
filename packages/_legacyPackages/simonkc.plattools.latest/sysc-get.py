import os
import platform

def get_available_commands():
    # Check if the platform is Windows
    if platform.system().lower() != 'windows':
        return ['Unsupported platform']

    # Get the system's PATH environment variable
    path = os.getenv("PATH")

    # Split the PATH variable into individual directories
    path_dirs = path.split(os.pathsep)

    # Initialize an empty list to store available commands
    available_commands = []

    # Define executable file extensions recognized by cmd on Windows
    cmd_executable_extensions = ['.exe', '.bat', '.cmd']

    # Iterate through each directory in the PATH
    for path_dir in path_dirs:
        try:
            # List all files in the directory
            files = os.listdir(path_dir)

            # Filter out only executable files with recognized extensions
            executable_files = [file for file in files if any(file.lower().endswith(ext) for ext in cmd_executable_extensions)]

            # Add the executable files to the list of available commands
            available_commands.extend(executable_files)

        except OSError:
            # Handle permission errors or other issues with accessing directories
            pass

    # Remove duplicates and sort the list of available commands
    available_commands = sorted(set(available_commands))

    return available_commands

# Example usage:
commands = get_available_commands()
print("Available commands:")
for command in commands:
    print(command)
