from colorama import Fore
from sys import exit


VERSION: str = '2.3.3'


def print_credit() -> None:
    print(Fore.BLUE + '''
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█▀▄▄▀█ ▄▄▀█▄ ▄█▀▄▀█ ████ ▄▄█ ▄▄▀
█ ▀▀ █ ▀▀ ██ ██ █▀█ ▄▄ █ ▄▄█ ▀▀▄
█ ████▄██▄██▄███▄██▄██▄█▄▄▄█▄█▄▄
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

    ''' + Fore.RESET)
    print(Fore.GREEN + 'made with ❤️ from simonecocco' + Fore.RESET + f'\nVersione: {VERSION}\n')

