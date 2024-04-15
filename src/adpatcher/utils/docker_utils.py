from adpatcher.utils.stdout_utils import error, output
from adpatcher.utils.process_utils import call_process
from adpatcher.utils.permission_utils import is_root_user
from adpatcher.utils.file_utils import is_valid_directory
from adpatcher.utils.path_utils import get_patcher_service_file_path
from json import dumps, loads
from adpatcher.services import Service
from os import getcwd, listdir, abspath
from os.path import join

def scan_for_docker_services(verbose: bool=False) -> list:
    def split_docker_output_in_information(row: str) -> dict:
        s: str = row.split(',')
        return {
            'id':s[0].split(':')[1],
            'name':s[1].split(':')[1],
            'status':s[2].split(':')[1],
            'ports':s[3].split('PORTS:')[1]
        }

    if not is_root_user():
        error('Devi essere root per eseguire questa operazione')
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

    docker_services_dir = [
        join(path, candidate_directory)
        for candidate_directory in listdir(path)
        if is_valid_directory(join(path, candidate_directory))
        if 'patcher' not in join(path, candidate_directory)
    ]
    return docker_services_dir

def create_docker_service_objects(verbose: bool=False, dockerv2: bool=False) -> list:
    docker_active_services: list = sorted(scan_for_docker_services(verbose), key=lambda service: service['name'])
    docker_disk_services: list = sorted(scan_for_docker_services_in_filesystem(None, verbose))
    complete_service_list: list = [
        Service(abspath(disk_directory_path), service['ports'], service['name'], disk_directory_path.lower(), dockerv2=dockerv2, verbose=verbose)
        for (service, disk_directory_path) in zip(docker_active_services, docker_disk_services)
    ]
    with open(get_patcher_service_file_path(), 'w') as f:
        f.write(dumps([service.to_dict() for service in complete_service_list]))
    output(f'Servizi mappati e salvati in {get_patcher_service_file_path()}', verbose)
    return complete_service_list

def load_services_from_json(verbose: bool=False, dockerv2: bool=False) -> list:
    with open(get_patcher_service_file_path(), 'r') as f:
        tmp = '\n'.join(f.readlines())
    return [Service(d['disk_path'], d['port'], d['name'], d['alias'], vulnerable_file=d['vulnerable_file'], dockerv2=dockerv2, verbose=verbose) for d in loads(tmp)]
