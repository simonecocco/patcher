from adpatcher.services import Service

def select_service_by_alias(services_list: list[Service], alias: str) -> Service|None:
    for service in services_list:
        all_service_names: list[str] = [service.abs_disk_path, service.alias, service.name, str(service.port[1])]
        if alias in all_service_names:
            return service
    else:
        return None

def get_service_alias_from_path(services_list: list, current_file_path: str) -> Service|None:
    # TODO ottieni il servizio secondo quello che è presente nel path
    pass