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

# prendi da file?
if (file_cmd:=['-f', '--file']) in p:
    file_name: str = p[file_cmd]
    if not is_valid_file(file_name):
        print('File non disponibile')
        exit(-1)
    f = open(file_name, 'r')
    instructions: list[str] = [instr for x in f.readlines() if len(instr:=x.strip()) > 2]
    f.close()
    Core(instructions, verbose=['-v', '--verbose'] in p, interactive=)
else:
    Core([i for i in p.__params__], verbose=['-v', '--verbose'] in p, interactive=not '-y' in p)

#TODO parte di docker
