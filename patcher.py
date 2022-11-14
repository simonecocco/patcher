#!/usr/bin/python3

import re
from sys import exit
from params import Params
from utils import is_valid_file
import credits
from service import Service, JSON_FILE_NAME, __saveservices__, get_services
from makefile import Makefile
from os.path import join
import os

p: Params = Params(help_description=credits.help, exit_if_no_args=False)
interactive: bool = not '-y' in p
verbose: bool = ['-v', '--verbose'] in p
quiet: bool = '-q' in p
services_list: list[Service]

# ---

if len(p) == 0:
    services_list = get_services(p.__scriptpath__, update=True)
    for service in services_list:
        Makefile(service.path)
    exit(0)
else:
    services_list = get_services(p.__scriptpath__)

# ---

if 'configure' in p:
    try:
        for service in services_list:
            print(f'Servizio:{service.name}, path:{service.path}, porta(int, out):{service.port}')
            tmp: str = input('imposta alias per il servizio: (o vuoto per skip) ')
            if len(tmp) > 0:
                service.alias = tmp
    except KeyboardInterrupt:
        pass

    __saveservices__(os.path.join(p.__scriptpath__, JSON_FILE_NAME), services_list)
    exit(0)

# ---
#TODO

#opzione checkpoint