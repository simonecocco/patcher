from colorama import Fore, Back

verbose: bool = True


def __template__(log_msg: str , msg: str, color: str = '') -> None:
    print(color + f'Log ({log_msg}): {msg}' + Fore.RESET)


def output(msg: str, ec: bool = False) -> None:
    if not verbose:
        return
    if ec:
        print(Back.BLUE + msg + Back.RESET)
    else:
        __template__('output', msg)


def debug(msg: str) -> None:
    __template__('debug', msg, color=Fore.GREEN)


def warning(msg: str) -> None:
    __template__('warning', msg, color=Fore.YELLOW)


def error(msg: str) -> None:
    __template__('error', msg, color=Fore.RED)


def diff_output(title1: str, text1: str, title2: str, text2: str) -> None:
    def __innerecprint__(back: str, fore: str, msg: str):
        print(back + fore + f'\n{msg}\n' + Fore.RESET + Back.RESET)
    output(title1, ec=True)
    __innerecprint__(Back.BLACK, Fore.WHITE, f'{text1}\n')
    output(title2, ec=True)
    __innerecprint__(Back.WHITE, Fore.BLACK, f'{text2}\n')
