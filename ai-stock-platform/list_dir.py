import os

def print_directory_tree(start_path, indent=""):
    """
    Recursively prints the directory tree starting from start_path.
    """
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent_str = ' ' * 4 * level
        print(f"{indent_str}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

if __name__ == "__main__":
    # Replace '.' with your desired path, e.g., './api'
    print_directory_tree('.')