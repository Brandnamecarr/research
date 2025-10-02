import os

files_by_folder = {}
extensions_to_ignore = [".git", ".gitignore", ".md", ".txt", ".csv", ".exe", ".so", ".o", ".pyc", ".ipynb"]
root_dir = "../.."

# print(os.listdir(root_dir))

for foldername, subfolders, filenames in os.walk(root_dir):
    relative_folder = os.path.relpath(foldername, root_dir)
    folder_key = "." if relative_folder == "." else relative_folder
    files_by_folder[folder_key] = filenames


for folder, files in files_by_folder.items():
    print(f"\n {folder}")
    for file in files:
        print(f"    -{file}")