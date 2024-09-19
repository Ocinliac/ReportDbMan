import os
import shutil


def archive_file(file_path, folder_path):
    archive_folder = os.path.join(folder_path, 'archive')
    if not os.path.exists(archive_folder):
        os.makedirs(archive_folder)

    file_name = os.path.basename(file_path)
    archive_path = os.path.join(archive_folder, file_name)
    shutil.move(file_path, archive_path)
    print(f"File '{file_name}' archived to '{archive_folder}'.")