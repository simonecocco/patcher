from adpatcher.services import Service
from typing import Union, List
from adpatcher.utils.file_utils import is_valid_file
from os.path import abspath, commonpath, join

def select_service_by_alias(services_list: list[Service], alias: str) -> Union[Service, None]:
    alias = alias.lower()
    for service in services_list:
        all_service_names: list[str] = [service.abs_disk_path.lower(), service.alias.lower(), service.name.lower(), str(service.port)]
        if any(alias in name for name in all_service_names):
            return service
    
    else:
        return None

def get_service_alias_from_path(services_list: list, current_file_path: str) -> Union[None, list]:
    if services_list is None or len(services_list) == 0:
        return None
    if is_valid_file(current_file_path): # Gestisce i path relativi o assoluti
        current_file_path = abspath(current_file_path)
        for service in services_list:
            service_path: str = commonpath([service.abs_disk_path, current_file_path])
            if service_path == service.abs_disk_path:
                return [service, current_file_path]
        else:
            return None
    elif '@' in current_file_path: # Gestisce per alias '[serv_name o alias]@path/to/file'
        serv_name, file_path = current_file_path.split('@', maxsplit=1)
        for service in services_list:
            if service.alias == serv_name or service.name == serv_name:
                return [service, join(service.abs_disk_path, file_path)]
        else:
            return None
    elif ':' in current_file_path: # Gestisce per porta 'porta:path/to/file'
        serv_name, file_path = current_file_path.split(':', maxsplit=1)
        for service in services_list:
            if str(service.port) == serv_name:
                return [service, join(service.abs_disk_path, file_path)]
        else:
            return None
    else:
        return None