from json import dumps, loads
from os import path
from utils import is_valid_file

class Service:
    def __init__(self, directory: str, name: str, in_port: str, out_port: str) -> None:
        self.path: str = directory
        self.name: str = name
        self.alias: str = name
        self.port: tuple[int, int] = (int(in_port), int(out_port))

    def service_copy() -> int: #ritorna la versione
        pass

    def restore_bkp(target_version: int, skip_files: list[str], interactive: bool = True) -> None:
        pass

    #TODO

JSON_FILE_NAME: str = 'services.json'

def __restorefromjson__(path: str) -> list[Service]:
    pass

def __getfromdocker__(path: str) -> list[Service]:
    pass

def __saveservices__(path: str, services: list[Service]) -> None:
    save_path: str = path.join(path, JSON_FILE_NAME)
    with open(save_path, 'w') as config:
        config.write(dumps(services))
        config.close()

def get_services(path: str) -> list[Service]:
    script_path: str = path.join(path, JSON_FILE_NAME)
    tmp: list[Service] = __restorefromjson__(path) if is_valid_file(script_path) else __getfromdocker__(path)
    __saveservices__(path, tmp)
    return tmp
