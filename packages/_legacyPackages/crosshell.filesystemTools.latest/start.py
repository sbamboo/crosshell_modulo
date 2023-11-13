import os
import subprocess
import platform
import sys

custom_path = argv[0]

# Check if the file path doesn't exist
if not os.path.exists(custom_path) or not os.sep in custom_path:
    # Join it with the current working directory
    current_dir = csSession.data.get("dir", os.getcwd())  # Replace 'csSession' with your actual session or data source
    custom_path = os.path.join(current_dir, custom_path)

if platform.system() == "Windows":
    # Open the file with the default application
    os.startfile(custom_path)
else:
    # Run the file using subprocess for Unix-like systems
    try:
        subprocess.run([custom_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print(custom_path)
        print(f"File not found: {custom_path}")
