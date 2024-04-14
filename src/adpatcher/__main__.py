from sys import argv
from argparse import ArgumentParser
from adpatcher.credits import print_credit
from adpatcher.utils import *

ACTIONS = {
    'reconfigure': lambda: None,
    'sos': lambda: None,
    'fixed': lambda: None,
    'service': lambda: None,
    'edit': lambda: None,
    'sysadmin': lambda: None,
}

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

    ACTIONS.get(args.params[0], lambda *args, **argk: print('Opzione inesistente'))()
