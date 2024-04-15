from os.path import exists, isfile, isdir
from os import access, R_OK

def is_valid_file(file_path: str) -> bool:
    return exists(file_path) and isfile(file_path) and access(file_path, R_OK)

def is_valid_directory(directory_path: str) -> bool:
    return exists(directory_path) and isdir(directory_path) and access(directory_path, R_OK)