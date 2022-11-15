#!/usr/bin/python3

import re
from sys import exit
from params import Params
from utils import is_valid_file, call_process
import credits
from service import Service, JSON_FILE_NAME, __saveservices__, get_services, search_for_service
from makefile import Makefile
from os.path import join
import os
import log

p: Params = Params(help_description=credits.help, exit_if_no_args=False)
interactive: bool = not '-y' in p
verbose: bool = ['-v', '--verbose'] in p
log.verbose = verbose
quiet: bool = '-q' in p
services_list: list[Service]
do_backup: bool = not '--no-bkp' in p
docker_update: bool = not '--no-docker' in p
docker_hard: bool = '--hard-build' in p
strict: bool = '--strict' in p

# ---

if len(p) == 0:
    services_list = get_services(p.__currentdir__, p.__scriptpath__, update=True)
    for service in services_list:
        Makefile(service.path)
        service.service_copy()
    exit(0)
else:
    services_list = get_services(p.__currentdir__, p.__scriptpath__)

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

if 'checkpoint' in p:
    target: list[str] = [x.lower() for x in p.__params__[1:]]
    for t in target:
        for s in services_list:
            if t in s.name or t == s.alias:
                print(f'Checkpoint di {s.name} ({s.alias})')
                s.service_copy()
    exit(0)

# ---

def parse_instruction(instruction: str) -> list:
    if '=' in instruction: 
        old_file, new_file = instruction.split('=')
        try:
            i = int(new_file)
            return old_file, i
        except:
            return old_file, new_file
    else:
        return instruction, None

listed_services: list[Service] = []
for instr in list(filter(lambda x: x[0] != '-', p.__params__)):
    param1, param2 = parse_instruction(instr)
    result = search_for_service(param1, services_list)
    if result is None:
        if strict:
            log.error(f'Istruzione non valida ({instr})')
            exit(1)
        else:
            log.warning(f'Istruzione non valida, skipped ({instr})')
            continue
    serv, param1 = result
    serv.instr.append((param1, param2))
    if serv not in listed_services:
        listed_services.append(serv)

for serv in listed_services:
    serv.execute_instruction(interactive, do_backup, docker_update, docker_hard, strict)