#!/usr/bin/python3

import re
import config
from sys import exit

from params import Params
from utils import is_valid_file
from core import Core
import credits
from service import *

p: Params = Params(help_description=credits.help, exit_if_no_args=False)
interactive: bool = not '-y' in p
verbose: bool = ['-v', '--verbose'] in p
quiet: bool = '-q' in p

# ---

if len(p) == 0:
    services_list: list[Service] = get_services(p.__scriptpath__)
    exit(0)

# ---

if 'configure' in p:
    for service in services_list:
        print(f'Servizio:{service.name}, path:{service.path}, porta(int, out):{service.port}')
        tmp: str = input('imposta alias per il servizio: (o vuoto per skip) ')
        if len(tmp) > 0:
            service.alias = tmp
    __saveservices__(services_list)
    exit(0)

# ---
#TODO