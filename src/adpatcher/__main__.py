import sys
from argparse import ArgumentParser


def main() -> None:
    pass

if __name__ == '__main__':
    aparse: ArgumentParser = ArgumentParser('patcher')
    aparse.add_argument('params', type=str, nargs='+',
                        help='Parametri di input')
    aparse.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        help='Non stampa i crediti')
    aparse.add_argument('-s', '--solve-checkpoint', action='store_true', dest='solve_checkpoint',
                        help='Fa diventare le modifiche definitive e imposta le patch come completate')
    aparse.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help='Mostra i dettagli delle operazioni')
    aparse.add_argument('-y', action='store_true', dest='auto_confirm',
                        help='Conferma automaticamente le modifiche')
    aparse.add_argument('-d2', dest='docker2', action='store_true',
                        help='Configura patcher per lavorare con docker compose v2 (di default lavora con la versione 1)')
    aparse.add_argument('-N', '--no-docker', dest='no_docker', action='store_true',
                        help='Non esegue operazioni su docker')
    main(args)
