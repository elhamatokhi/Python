import os 

"""
File System Operations Script - file handling using the os module
"""

# Display the current working directory
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")

# Define folder and file names
folder_name = "lab_files"
file_names = ["file1.txt", "file2.txt", "file3.txt"]

# Create the folder if it does not exist
if not os.path.exists(folder_name):
    os.mkdir(folder_name)
    print(f'Folder "{folder_name}" created.')
else:
    print(f'Folder "{folder_name}" already exists.')

# Create empty text files inside the folder
for file in file_names:
    file_path = os.path.join(folder_name, file)
    open(file_path, 'w').close() # Create empty file
    print(f'File "{file}" created.')

# List all files in the folder
print("\nFiles in folder:")
files = os.listdir(folder_name)
for file in files:
    print(file)

# Rename one of the files
old_name = os.path.join(folder_name, "file1.txt")
new_name = os.path.join(folder_name, 'renamed_file.txt')

if os.path.exists(old_name):
    os.rename(old_name,new_name)
    print('\nFile "file1.txt" renamed to "renamed_file.txt".')

# Clean up: remove files and folder
for file in os.listdir(folder_name):
    os.remove(os.path.join(folder_name,file))
    print(f'File "{file}" removed.')

os.rmdir(folder_name)
print(f'Folder "{folder_name}" removed. Cleanup complete.')