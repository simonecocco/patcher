import os
from subprocess import call, Popen, PIPE
from adpatcher.log import error, output
from adpatcher.services import Service
from json import dumps, loads

GIT_MASTER_BRANCH_NAME: str = 'master'
GIT_ORIGINAL_BRANCH_NAME: str = 'original'

def is_root_user() -> bool:
    """
    controlla se l'utente è root
    :return: True se è root
    """
    return os.geteuid() == 0

def is_valid_file(file_path: str, is_file: bool=True, readable: bool=True):
    """
    controlla se il file è valido
    :param file_path: path del file da controllare
    :param is_file: True per verificare che sia un file
    :param readable: True per verificare che sia leggibile
    :return: ritorna True se soddisfa le condizioni specificate (e soprattutto che esista)
    """
    exist: bool = os.path.exists(file_path)
    file: bool = not is_file or os.path.isfile(file_path) if exist else False
    can_read: bool = not is_file or not readable or open(file_path, 'r').readable() if exist else False
    return file and can_read

def get_makefile_path_for_service(service_path: str) -> str:
    return service_path if service_path.endswith('makefile') else os.path.join(service_path, 'makefile')

def call_process(cmd: str, params: list=[]) -> list:
    """
    chiama un processo
    :param cmd: chiamata
    :param params:
    :return: stdout, stderr
    """
    _process: Popen = Popen([cmd] + params, stdout=PIPE, stderr=PIPE)
    _stdout, _stderr = _process.communicate()
    return [_stdout.decode('utf-8'), _stderr.decode('utf-8')]


def do_checkpoint_backup(service_path: str) -> None:
    """
    Crea una copia della cartella al di fuori del percorso specificato
    copiando tutta la struttura presente. Utile in caso di eliminazione non programmata.
    """
    if not (os.path.exists(service_path) and os.path.isdir(service_path)):
        error(f'{service_path} non valida')
        exit(1)
    prefix: str = '/'.join((tmp := service_path.split('/'))[:-1])
    service_name: str = tmp[-1]
    count: int = 0
    backup_path: str
    while True:
        backup_path = os.path.join(prefix ,f'.{service_name}_bkp{count}')
        if os.path.exists(backup_path):
            count += 1
        else:
            break
    
    call_process('cp', ['-r', service_path, backup_path, '--preserve=mode,ownership,timestamps'])

def git_config(username: str='Patcher', email: str='patcher@localhost') -> None:
    """
    Configura git
    :param username: nome utente
    :param email: email
    """
    call_process('git', ['config', 'user.name', username], directory_path)
    call_process('git', ['config', 'user.email', email], directory_path)

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
        if select is None or select in output_row
    ]

def get_home_directory() -> str:
    return os.path.expanduser('~')

def get_patcher_home_directory() -> str:
    patcher_dir_path = os.path.join(get_home_directory(), '.patcher')
    if not os.path.exists(patcher_dir_path):
        os.mkdir(patcher_dir_path)
    return patcher_dir_path

def get_patcher_service_file_path() -> str:
    return os.path.join(get_patcher_home_directory(), 'services.json')

def scan_for_docker_services_in_filesystem(path: [str, None], verbose: bool=False) -> list:
    output('Localizzazione servizi su disco', verbose=verbose)

    if path is None:
        path = os.getcwd() if 'patcher' not in os.getcwd() else os.path.join(os.getcwd(), '..')

    docker_services_dir = [
        os.path.join(path, candidate_directory)
        for candidate_directory in os.listdir(path)
        if os.path.exists(os.path.join(path, candidate_directory))
        if os.path.isdir(os.path.join(path, candidate_directory))
        if 'patcher' not in os.path.join(path, candidate_directory)
    ]
    return docker_services_dir
    
def create_docker_service_objects(verbose: bool=False, dockerv2: bool=False) -> list:
    docker_active_services: list = sorted(scan_for_docker_services(verbose), key=lambda service: service['name'])
    docker_disk_services: list = sorted(scan_for_docker_services_in_filesystem(None, verbose))
    complete_service_list: list = [
        Service(os.path.abspath(disk_directory_path), service['ports'], service['name'], disk_directory_path.lower(), dockerv2=dockerv2, verbose=verbose)
        for (service, disk_directory_path) in zip(docker_active_services, docker_disk_services)
    ]
    with open(get_patcher_service_file_path(), 'w') as f:
        f.write(dumps([service.to_dict() for service in complete_service_list]))
    output(f'Servizi mappati e salvati in {get_patcher_service_file_path()}', verbose)
    return complete_service_list

def set_main_git_branch_name() -> None:
    call_process('git', ['branch', '-M', GIT_MASTER_BRANCH_NAME])

def create_copy_of_original_service() -> None:
    call_process('git', ['add', '-A'])
    call_process('git', ['commit', '-a', '-m', 'Original service'])
    call_process('git', ['branch', '-C', GIT_MASTER_BRANCH_NAME, GIT_ORIGINAL_BRANCH_NAME])
    call_process('git', ['checkout', GIT_MASTER_BRANCH_NAME])

def create_new_git_branch(branch_name: str, checkout: bool=True) -> None:
    call_process('git', ['branch', '-C', 'master', branch_name])
    if checkout:
        call_process('git', ['checkout', branch_name])

def git_update_file() -> None:
    call_process('git', ['add', '--update'])

def git_commit(message: str='Bug fixing') -> None:
    # TODO aggiungi LLM che si metta a generare un messaggio di commit
    call_process('git', ['commit', '-a', '-m', message])

def git_rollback(how_many) -> None:
    call_process('git', ['reset', '--hard', f'HEAD~{how_many}'])

def git_save_stash() -> None:
    call_process('git', ['stash', 'save'])

def git_apply_stash() -> None:
    call_process('git', ['stash', 'apply'])

def git_change_branch(branch_name: str, ) -> None:
    git_save_stash()
    call_process('git', ['checkout', branch_name])
    git_apply_stash()

def git_merge_into_main_branch() -> None:
    call_process('git', ['merge', GIT_MASTER_BRANCH_NAME, 'quarantine'])

def check_for_uncompleted_merges() -> list:
    raw_text, _ = call_process('git', ['status', '-s'])
    if len(raw_text) == 0:
        return []
    return [file_name.split(' ', maxsplit=1)[1] for file_name in raw_text.strip().split('\n')]

def solve_merge_conflicts() -> None:
    # TODO implementa la risoluzione automatica dei conflitti
    call_process('git', ['mergetool'])

def load_services_from_json(dockerv2: bool=False) -> list:
    with open(get_patcher_service_file_path(), 'r') as f:
        tmp = '\n'.join(f.readlines())
    return [Service(d['disk_path'], d['port'], d['name'], d['alias'], vulnerable_file=d['vulnerable_file'], dockerv2=dockerv2, verbose=verbose) for d in loads(tmp)]
