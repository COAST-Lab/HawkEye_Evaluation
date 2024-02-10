import os

def rename_sig_to_txt(file_path):
    # Compute the new file name by replacing the .sig extension with .txt
    new_file_path = file_path.replace('.sig', '.txt')
    os.rename(file_path, new_file_path)

def main():
    # Iterate over all files in the current directory
    for file_name in os.listdir('.'):
        if file_name.endswith('.sig'):
            rename_sig_to_txt(file_name)

if __name__ == "__main__":
    main()
