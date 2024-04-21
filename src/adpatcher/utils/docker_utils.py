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

def create_docker_service_objects(path: str='', verbose: bool=False, dockerv2: bool=False) -> list:
    docker_active_services: list = sorted(scan_for_docker_services(verbose), key=lambda service: service['name'])
    docker_disk_services: list = sorted(scan_for_docker_services_in_filesystem(path=path, verbose=verbose), key=lambda service: service.split('/')[-1])
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
        else:
            complete_service_list.append(
                Service(
                    abspath(docker_disk_service),
                    candidates[0]['ports'],
                    candidates[0]['name'],
                    docker_disk_service.lower(),
                    dockerv2=dockerv2, verbose=verbose
                )
            )

    with open(get_patcher_service_file_path(), 'w') as f:
        f.write(dumps([service.__dict__() for service in complete_service_list]))
    output(f'Servizi mappati e salvati in {get_patcher_service_file_path()}', verbose)
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
