from colorama import Fore
from sys import exit


VERSION: str = '2.0.0-alpha'


def print_credit() -> None:
    print(Fore.BLUE + '''
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█▀▄▄▀█ ▄▄▀█▄ ▄█▀▄▀█ ████ ▄▄█ ▄▄▀
█ ▀▀ █ ▀▀ ██ ██ █▀█ ▄▄ █ ▄▄█ ▀▀▄
█ ████▄██▄██▄███▄██▄██▄█▄▄▄█▄█▄▄
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

    ''' + Fore.RESET)
    print(Fore.GREEN + 'made with ❤️ from d1dpvl' + Fore.RESET + f'\nVersione: {VERSION}\n')


def print_help() -> None:
    print('''come usarlo:
    [apply a] [path del vecchio file] [path del file] OPZIONI
    [back b] [path del file] [numero versione] OPZIONI
    [file f] [file con le modifiche multiple] OPZIONI

    OPZIONI

    -q -> non stampa i crediti
    --no-bkp -> non fa il backup del file che si va a sostituire
    --no-docker -> non fa il build del container
    --hard-build -> esegue un docker-compose down e poi up. Non funziona se --no-docker è presente
    --back -> al posto di applicare la patch, torna una versione indietro per tutti i file (può essere usato solo con 'f')

    ''')
    exit(0)
