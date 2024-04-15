from sys import argv
from argparse import ArgumentParser
from adpatcher.credits import print_credit
from adpatcher.utils.docker_utils import *
from adpatcher.utils.file_utils import is_valid_file
from adpatcher.utils.stdout_utils import error, warning

ACTIONS = [
    'reconfigure'
    'sos'
    'fix'
    'service'
    'edit'
    'sysadmin'
]

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
    args = aparse.parse_args(argv[1:])

    if not args.quiet:
        print_credit()

    services: list = load_services_from_json(args.docker2)\
        if is_valid_file(get_patcher_service_file_path())\
        else create_docker_service_objects(args.verbose, dockerv2=args.docker2)

    user_action: str = args.params[0]
    if user_action not in ACTIONS:
        print(f'Errore: azione non riconosciuta: {user_action}')
        exit(1)
    elif user_action == 'reconfigure':
        pass
    elif user_action == 'sos':
        for target_service_alias in args.params[1:]:
            current_selected_service: Service = select_service_based_on_alias(services, target_service_alias)
            if current_selected_service is None:
                error(f'Servizio non trovato: {target_service_alias}')
                continue
            warning(f'Servizio {current_selected_service.alias} in modalità sos')
            current_selected_service.sos()
            output(f'Servizio {current_selected_service.alias} in modalità sos completato', verbose=args.verbose)
    elif user_action == 'fix':
        pass
    elif user_action == 'service':
        pass
    elif user_action == 'edit':
        pass
    elif user_action == 'sysadmin':
        pass

