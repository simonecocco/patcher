from argparse import ArgumentParser

def configure_argparse():
    aparse = ArgumentParser('patcher.py')
    aparse.add_argument('params', type=str, nargs='+')
    aparse.add_argument('-q', '--quiet', action='store_true', dest='quiet')
    aparse.add_argument('--no-bkp', action='store_true', dest='no_bkp')
    aparse.add_argument('--no-docker', action='store_true', dest='no_docker')
    aparse.add_argument('--hard-build', action='store_true', dest='hard_build')
    aparse.add_argument('-v', '--verbose', action='store_true', dest='verbose')
    aparse.add_argument('-y', action='store_true', dest='yes', help='non chiede conferma per le modifiche')
    aparse.add_argument('-d2', action='store_true', dest='docker2', help='configura patcher per lavorare con docker compose v2 (di default lavora con la versione 1)')
    aparse.add_argument('--strict', action='store_true', dest='strict', help='si accerta che venga eseguita ogni operazione')

    return aparse

