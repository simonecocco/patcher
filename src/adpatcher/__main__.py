from os import getcwd
from sys import argv
from argparse import ArgumentParser
from adpatcher.credits import print_credit
from adpatcher.utils.docker_utils import *
from adpatcher.utils.file_utils import is_valid_file
from adpatcher.utils.stdout_utils import error, output
from adpatcher.utils.service_utils import *

def execute_configure_action(args) -> None:
    if len(args.params) == 1:
        create_docker_service_objects(path=getcwd(), verbose=args.verbose, dockerv2=args.docker2)
    else:
        print('Non sono supportate altre opzioni... per ora')
        exit(1)

def execute_sos_action(args, services: list[Service]) -> None:
    pass

def execute_fix_action(args, services: list[Service]) -> None:
    pass

def execute_service_action(args, services: list[Service]) -> None:
    pass

def execute_edit_action(args, services: list[Service]) -> None:
    pass

def execute_sysadmin_action(args, services: list[Service]) -> None:
    pass

def execute_action(args, services: list[Service]) -> None:
    user_action: str = args.params[0]
    
    if user_action == 'sos':
        execute_sos_action(args, services)
    elif user_action == 'fix':
        execute_fix_action(args, services)
    elif user_action == 'service':
        execute_service_action(args, services)
    elif user_action == 'edit':
        execute_edit_action(args, services)
    elif user_action == 'sysadmin':
        execute_sysadmin_action(args, services)
    else:
        print('Azione non riconosciuta')
        exit(1)

def main() -> None:
    aparse: ArgumentParser = ArgumentParser('patcher')
    aparse.add_argument('params', type=str, nargs='+',
                        help='Parametri di input')
    aparse.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        help='Non stampa i crediti')
    aparse.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help='Mostra i dettagli delle operazioni')
    aparse.add_argument('-y', action='store_true', dest='auto_confirm',
                        help='Conferma automaticamente le modifiche')
    aparse.add_argument('-d2', dest='docker2', action='store_true',
                        help='Configura patcher per lavorare con docker compose v2 (di default lavora con la versione 1)')
    aparse.add_argument('-N', '--no-docker', dest='no_docker', action='store_true',
                        help='Non esegue operazioni su docker')
    aparse.add_argument('-A', '--atomic', dest='atomic', action='store_true',
                        help='Esegue le operazioni in modo atomico')
    args = aparse.parse_args(argv[1:])

    if not args.quiet:
        print_credit()

    if len(args.params) == 0:
        error('Nessuna azione specificata')
        exit(1)

    if not is_valid_file(get_patcher_service_file_path()) and args.params[0] != 'configure':
        error('Primo avvio: esegui `patcher configure` per configurare i servizi')
        exit(0)

    if args.params[0] == 'configure':    
        execute_configure_action(args)
        exit(0)
    
    services: list = load_services_from_json(args.docker2)\
        if is_valid_file(get_patcher_service_file_path())\
        else create_docker_service_objects(args.verbose, dockerv2=args.docker2)

    execute_action(args, services)
