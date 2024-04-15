from os.path import join, expanduser
from os import mkdir
from adpatcher.utils.file_utils import is_valid_directory

def get_makefile_path_for_service(service_path: str) -> str:
    return service_path if service_path.endswith('makefile') else join(service_path, 'makefile')

def get_home_directory() -> str:
    return expanduser('~')

def get_patcher_home_directory() -> str:
    patcher_dir_path = join(get_home_directory(), '.patcher')
    if not is_valid_directory(patcher_dir_path):
        mkdir(patcher_dir_path)
    return patcher_dir_path

def get_patcher_service_file_path() -> str:
    return join(get_patcher_home_directory(), 'services.json')

