from os.path import exists, isfile, isdir
from os import access, R_OK

def is_valid_file(file_path: str) -> bool:
    """
    if not exists(file_path):
        print(f'Il file {file_path} non esiste')
        return False
    if not isfile(file_path):
        print(f'Il path {file_path} non è un file')
        return False
    if not access(file_path, R_OK):
        print(f'Il file {file_path} non è leggibile')
        return False
    return True
    """
    return exists(file_path) and isfile(file_path) and access(file_path, R_OK)

def is_valid_directory(directory_path: str) -> bool:
    return exists(directory_path) and isdir(directory_path) and access(directory_path, R_OK)