from typing import Union
from os import getcwd, stat
from sys import argv
from argparse import ArgumentParser
from adpatcher.credits import print_credit
from adpatcher.utils.docker_utils import *
from adpatcher.utils.file_utils import is_valid_file
from adpatcher.utils.stdout_utils import error, output, warning, debug
from adpatcher.utils.service_utils import *
from adpatcher.utils.permission_utils import is_docker_user, add_user_to_docker
from rich.live import Live
from re import match, Pattern

def check_min_len(params: list, min_len: int) -> None:
    if len(params) < min_len:
        error(f'Numero minimo di parametri non rispettato. Attesi {min_len}, ricevuti {len(params)}')
        exit(1)

# patcher configure
def execute_configure_action(args, before: bool=False) -> None:
    if len(args.params) == 1 or before:
        create_docker_service_objects(path=getcwd(), verbose=args.verbose, dockerv2=args.docker2)
    else:
        print('Non sono supportate altre opzioni... per ora')
        exit(1)

# patcher sos <list of services>
def execute_sos_action(args, services: list[Service]) -> None:
    check_min_len(args.params, 2)
    target_services: list[Service] = []
    for service_name in args.params[1:]:
        target_service: Union[Service, None] = select_service_by_alias(services, service_name)
        if target_service is None:
            if args.atomic:
                error('Servizio non trovato')
                exit(1)
            else:
                warning('Servizio non trovato')
                continue
        target_services.append(target_service)
    for service in target_services:
        warning(f'{service_name} in modalità emergenza')
        service.sos()

# patcher fix {path/alias/port} n
# patcher fix {path/alias/port}
def execute_fix_action(args, services: list[Service]) -> None:
    check_min_len(args.params, 2)
    target_service: Service|None = select_service_by_alias(services, args.params[1])
    if target_service is None:
        error('Servizio non trovato')
        exit(1)
    if len(args.params) == 2:
        if not args.auto_confirm:
            warning('Si vuole chiudere la quarantena? [Y/n] ')
            resp: str = input()
            if resp != 'Y':
                output('Operazione annullata', args.verbose)
                exit(0)
        target_service.close_quarantine()
    else:
        try:
            rollback_n: int = int(args.params[2])
        except:
            error('Numero di rollback non valido')
            exit(1)
        if rollback_n == 0:
            output('Sei già nel commit attuale', args.verbose)
            exit(0)
        if rollback_n < 0:
            rollback_n = -rollback_n

        target_service - rollback_n

# patcher services list
# patcher services tarball
# patcher services alias <service_name> <new_alias>
def execute_services_action(args, services: list[Service]) -> None:
    check_min_len(args.params, 2)
    sub_action: str = args.params[1]
    if sub_action == 'list':
        for i, service in enumerate(services):
            print(f'{i})', end=' ')
            service.pretty_print()
            print()
    elif sub_action == 'tarball':
        for service in services:
            output(f'Creo tarball per {service.name}', args.verbose)
            service.tarball(getcwd())
    elif sub_action == 'alias':
        check_min_len(args.params, 4)
        service_name: str = args.params[2]
        new_alias: str = args.params[3]
        target_service: Union[Service, None] = select_service_by_alias(services, service_name)
        if target_service is None:
            error('Servizio non trovato')
            exit(1)
        target_service.alias = new_alias
        output(f'Alias del servizio {target_service.name} cambiato in {new_alias}', args.verbose)
        write_services_on_json(services, args.verbose)

# patcher edit orig_file_path new_file
# patcher edit alias@relative_path new_file
# patcher edit port:relative_path new_file
def execute_edit_action(args, services: list[Service]) -> None: # TODO
    check_min_len(args.params, 3)

    couples = [(args.params[i], args.params[i+1]) for i in range(1, len(args.params), 2)]
    target_services: dict = {}
    for couple in couples:
        if not is_valid_file(couple[1]):
            if args.atomic:
                error(f'File {couple[1]} non valido')
                exit(1)
            else:
                warning(f'File {couple[1]} non valido')
                continue
        result = get_service_alias_from_path(services, couple[0])
        if result is None:
            if args.atomic:
                error(f'Servizio non trovato')
                exit(1)
            else:
                warning(f'Servizio non trovato')
                continue
        service, file_path = result
        target_services[service] = target_services.get(service, []) + [(file_path, couple[1])]
            
    for service, service_couples in target_services.items():
        output(f'Applico le modifiche al servizio {service.name}', args.verbose)
        service.apply_list_of_patches(service_couples, atomic=args.atomic)
        

# patcher sysadmin shadow <service name> <up time[seconds]> <down time[seconds]>
# patcher sysadmin info
def execute_sysadmin_action(args, services: list[Service]) -> None:
    check_min_len(args.params, 2)
    sub_action: str = args.params[1]
    if sub_action == 'shadow':
        check_min_len(args.params, 3)
        service_name: str = args.params[2]
        target_service: Union[Service, None] = select_service_by_alias(services, service_name)
        if target_service is None:
            error('Servizio non trovato')
            exit(1)
        warning(f'Avvio modalità shadow')
        while True:
            sleep(int(args.params[3]))
            warning('Stop del servizio')
            target_service('down')
            sleep(int(args.params[4]))
            warning('Avvio del servizio')
            target_service('shadow')
    elif sub_action == 'info':
        with Live(screen=True, auto_refresh=False) as live:
            live.console.print('Informazioni sui servizi')
            while True:
                services_status: list = combine_services_with_infos(services, get_services_status(), get_services_usages())
                status_string_to_print: str = 'Informazioni sui servizi\n\n'
                for i, service_status in enumerate(services_status):
                    status: int = service_status[1][1]
                    partial_status_string_to_print: str = f"{i}) {service_status[0].name} ({service_status[0].alias})\n\t{service_status[1][0]}\n\tCPU%: {service_status[2]['cpu']}\n\tMEM%: {service_status[2]['ram']}"
                    status_string_to_print += partial_status_string_to_print + '\n'
                live.console.clear()
                live.console.print(status_string_to_print)

def execute_action(args, services: list[Service]) -> None:
    user_action: str = args.params[0]
    
    if user_action == 'sos':
        execute_sos_action(args, services)
    elif user_action == 'fix':
        execute_fix_action(args, services)
    elif user_action == 'services':
        execute_services_action(args, services)
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

    if not is_docker_user():
        add_user_to_docker()

    if not is_valid_file(get_patcher_service_file_path()) or args.params[0] == 'configure':    
        execute_configure_action(args, before=args.params[0] != 'configure')
        exit(0)
    
    services: list = load_services_from_json(args.docker2)\
        if is_valid_file(get_patcher_service_file_path())\
        else create_docker_service_objects(args.verbose, dockerv2=args.docker2)

    try:
        execute_action(args, services)
    except:
        print('Bye! :)')
        exit(0)

