from adpatcher.utils.stdout_utils import error, output, warning
from adpatcher.utils.process_utils import call_process
from adpatcher.utils.permission_utils import is_root_user, is_docker_user
from adpatcher.utils.file_utils import is_valid_directory
from adpatcher.utils.path_utils import get_patcher_service_file_path
from json import dumps, loads
from adpatcher.services import Service
from os import getcwd, listdir
from os.path import join, abspath

def scan_for_docker_services(verbose: bool=False) -> list:
    def split_docker_output_in_information(row: str) -> dict:
        s: list[str] = row.split(',')
        return {
            'id':s[0].split(':')[1],
            'name':s[1].split(':')[1],
            'status':s[2].split(':')[1],
            'ports':s[3].split('PORTS:')[1]
        }

    if not is_root_user() and not is_docker_user():
        error('Devi essere root o abilitato a docker per eseguire questa operazione')
        exit(1)

    output('Caricamento servizi', verbose=verbose)
    raw_text, err = call_process('docker', [
        'ps',
        '--format',
        'table ID:{{.ID}},NAME:{{.Image}},STATUS:{{.Status}},PORTS:{{.Ports}}'
    ])

    if len(err) > 0:
        error(f'Errore durante la chiamata a docker.\nTraceback\n{err}')
        exit(1)

    output('Fatto', verbose)
    rows_of_output = raw_text.split('\n')[1:-1]
    return [
        split_docker_output_in_information(output_row)
        for output_row in rows_of_output
    ]

def scan_for_docker_services_in_filesystem(path: str='', verbose: bool=False) -> list:
    output('Localizzazione servizi su disco', verbose=verbose)

    if path == '':
        path = getcwd() if 'patcher' not in getcwd() else join(getcwd(), '..')

    docker_services_dir = []
    
    for candidate_directory in listdir(path): #TODO bug
        if candidate_directory is not None and\
            is_valid_directory(join(path, candidate_directory)) and\
            'patcher' not in join(path, candidate_directory):
            docker_services_dir.append(join(path, candidate_directory))

    return docker_services_dir

def join_docker_services_with_their_disk_path(docker_active_services, docker_disk_services, dockerv2: bool=False, verbose=False) -> list[Service]:
    complete_service_list: list[Service] = []
    for docker_disk_service in docker_disk_services:
        output(f'Servizio trovato su disco: {docker_disk_service}', True)
        candidates: list = [
            docker_active_service
            for docker_active_service in docker_active_services
            if docker_disk_service.split('/')[-1].lower() in docker_active_service['name'].lower()
        ]
        if len(candidates) > 1:
            warning('Trovati molteplici candidati, seleziona quello giusto')
            for i, candidate in enumerate(candidates):
                warning(f'{i} {candidate["name"]} {candidate["ports"]}',)
            selected: int = int(input(f'Numero [0..{len(candidates)-1}] ' ))
            complete_service_list.append(
                Service(
                    abspath(docker_disk_service),
                    candidates[selected]['ports'],
                    candidates[selected]['name'],
                    docker_disk_service.lower(),
                    dockerv2=dockerv2, verbose=verbose
                )
            )
        elif len(candidates) == 1:
            complete_service_list.append(
                Service(
                    abspath(docker_disk_service),
                    candidates[0]['ports'],
                    candidates[0]['name'],
                    docker_disk_service.lower(),
                    dockerv2=dockerv2, verbose=verbose
                )
            )
        else:
            warning(f'Nessun candidato trovato per {docker_disk_service}')    
    return complete_service_list

def write_services_on_json(complete_service_list: list[Service], verbose: bool=False) -> None:
    with open(get_patcher_service_file_path(), 'w') as f:
        f.write(dumps([service.__dict__() for service in complete_service_list]))
    output(f'Servizi mappati e salvati in {get_patcher_service_file_path()}', verbose)

def create_docker_service_objects(path: str='', verbose: bool=False, dockerv2: bool=False) -> list:
    docker_active_services: list = sorted(scan_for_docker_services(verbose), key=lambda service: service['name'])
    docker_disk_services: list = sorted(scan_for_docker_services_in_filesystem(path=path, verbose=verbose), key=lambda service: service.split('/')[-1])
    complete_service_list: list[Service] = join_docker_services_with_their_disk_path(docker_active_services, docker_disk_services, dockerv2=dockerv2, verbose=verbose)
    
    write_services_on_json(complete_service_list, verbose=verbose)
    return complete_service_list

def load_services_from_json(verbose: bool=False, dockerv2: bool=False) -> list:
    with open(get_patcher_service_file_path(), 'r') as f:
        tmp = '\n'.join(f.readlines())
    return [Service(d['disk_path'], d['port'], d['name'], d['alias'], vulnerable_file=d['vulnerable_file'], dockerv2=dockerv2, verbose=verbose) for d in loads(tmp)]

def select_service_based_on_alias(services_list: list, alias: str) -> Service|None:
    for service in services_list:
        if alias in [service.alias, service.name, service.abs_disk_path]:
            return service
    return None

def get_services_status():
    raw_containers_status, _ = call_process('docker', ['ps', '-a', '--format', 'table {{.Names}}    {{.Status}}'])
    containers_status = [
        row.split('    ')
        for row in raw_containers_status.split('\n')[1:]
        if len(row) > 0
    ]
    return containers_status

def get_services_usages():
    raw_container_resources, _ = call_process('docker', ['stats', '--no-stream', '--format', 'table {{.Name}}    {{.CPUPerc}}    {{.MemPerc}}'])
    container_resources = [
        row.split('    ')
        for row in raw_container_resources.split('\n')[1:]
        if len(row) > 0
    ]
    return container_resources

def valutate_container_status(status: str) -> list:
    status = status.lower().split(' ')[0]
    return {
        'created': ['container up ma non avviato', 1],
        'running': ['container completamente attivo', 1],
        'paused': ['container up ma in pausa', 0],
        'exited': ['container terminato', -1],
        'dead': ['container morto', -1],
        'restarting': ['container in riavvio', 0],
        'removing': ['container in rimozione', -1],
        'removed': ['container rimosso', -1],
        'up': ['container completamente attivo', 1],
        'down': ['container non in esecuzione', -1],
        'oomkilled': ['container ucciso per troppa memoria consumata', -1],
        'crashed': ['container crashato', -1]
    }.get(status, [status, 0])

def combine_services_with_infos(services: list[Service], containers_status: list, containers_resources: list) -> list:
    services_status: list = []
    #services = sorted(services, key=lambda service: service.name.lower())
    #containers_status = sorted(containers_status, key=lambda container: container[0].lower())
    #containers_resources = sorted(containers_resources, key=lambda container: container[0].lower())
    for service in services:
        complete_info: list = [service]
        for container_status in containers_status:
            if service.name.lower() in container_status[0].lower() or container_status[0].lower() in service.name.lower():
                complete_info.append(valutate_container_status(container_status[1]))
                break
        else:
            complete_info.append(['container non trovato', -1])
        for container_resource in containers_resources:
            if service.name.lower() in container_resource[0].lower() or container_resource[0].lower() in service.name.lower():
                complete_info.append({'cpu':container_resource[1], 'ram':container_resource[2]})
                break
        else:
            complete_info.append({'cpu':'non disponibile', 'ram':'non disponibile'})
        if len(complete_info) == 3:
            services_status.append(complete_info)
    return services_status
    