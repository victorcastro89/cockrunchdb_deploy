import os


def extract_python_files(start_path='.'):
    """
    Recursively find all .py files from the start_path and format their contents.

    Args:
        start_path (str): The directory path to start searching from. Defaults to current directory.

    Returns:
        str: Formatted string containing all Python file contents with their paths as headers
    """
    output = []

    # Walk through all directories
    for root, dirs, files in os.walk(start_path):
        # Filter for .py files
        python_files = [f for f in files ]

        for py_file in python_files:
            # Get the full file path
            file_path = os.path.join(root, py_file)
            if file_path.endswith('get_src.py'):
                continue
            try:
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Format the output
                file_header = f"#{file_path}"

                # Add to output list with proper spacing
                output.extend([
                    file_header,
                    content,
                    ''  # Empty line for separation
                ])

            except Exception as e:
                output.extend([
                    f"#{file_path}",
                    f"Error reading file: {str(e)}",
                    ''
                ])

    # Join all parts with newlines
    return '\n'.join(output)


def save_output(formatted_content, output_file='python_files_content.txt'):
    """
    Save the formatted content to a file.

    Args:
        formatted_content (str): The formatted string containing all Python file contents
        output_file (str): The name of the output file. Defaults to 'python_files_content.txt'
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        print(f"Successfully saved output to {output_file}")
    except Exception as e:
        print(f"Error saving to file: {str(e)}")


if __name__ == '__main__':
    # Get formatted content starting from current directory
    formatted_content = extract_python_files()

    # Save to file
    save_output(formatted_content)