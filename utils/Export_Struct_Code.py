import os

def print_python_files_code(root_dir, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = ["__pycache__", "venv", ".venv", ".idea", ".git"]

    try:
        files = os.listdir(root_dir)
    except PermissionError:
        return

    for f in sorted(files):
        path = os.path.join(root_dir, f)
        if os.path.isdir(path):
            if f not in exclude_dirs:
                print_python_files_code(path, exclude_dirs)
        elif f.endswith(".py"):
            print(f"\n# File: {path}\n")
            with open(path, "r") as file:
                print(file.read())
            print("\n" + "#" * 40 + "\n")

# Replace 'your_project_path' with the actual path of your project
root_directory = "/Users/nicolascailmail/PyProject/ReportDbMan/gui/modules"
print_python_files_code(root_directory)
