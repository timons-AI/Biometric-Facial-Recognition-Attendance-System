import os

def should_exclude(root, exclude_dirs):
    for exclude in exclude_dirs:
        if root.startswith(exclude):
            return True
    return False

def get_directory_tree(root_dir, exclude_dirs):
    tree_lines = []
    for root, dirs, files in os.walk(root_dir):
        if should_exclude(root, exclude_dirs):
            continue
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        tree_lines.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            tree_lines.append(f"{sub_indent}{file}")
    return "\n".join(tree_lines)

def write_codebase_to_file(root_dir, output_file, exclude_dirs):
    with open(output_file, 'w', encoding='utf-8') as f_out:
        # Write directory tree
        f_out.write("Directory Structure:\n")
        f_out.write("=" * 80 + "\n")
        f_out.write(get_directory_tree(root_dir, exclude_dirs))
        f_out.write("\n" + "=" * 80 + "\n\n")
        
        # Write file contents
        for root, dirs, files in os.walk(root_dir):
            if should_exclude(root, exclude_dirs):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, root_dir)
                
                f_out.write(f"File: {relative_path}\n")
                f_out.write('-' * 80 + '\n')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f_in:
                        f_out.write(f_in.read())
                except Exception as e:
                    f_out.write(f"Error reading file: {e}\n")
                
                f_out.write('\n' + '=' * 80 + '\n\n')

if __name__ == "__main__":
    root_directory = input("Enter the root directory of your code base: ")
    output_filename = input("Enter the output text file name (without .txt extension): ") + '.txt'
    exclude_dirs_input = input("Enter folders to exclude (full paths), separated by commas: ")
    exclude_dirs = [dir.strip() for dir in exclude_dirs_input.split(',')]
    write_codebase_to_file(root_directory, output_filename, exclude_dirs)
    print(f"Code base has been written to {output_filename}")
