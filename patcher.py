#!/usr/bin/python3

import re
import config
from sys import exit

from params import Params
from utils import is_valid_file
from core import Core

p: Params = Params()

def get_config() -> None:
    global p
    if len(p) == 1:
        serv: dict = {}
        try:
            while True:
                path: str
                name: str
                path = input('Path: ')
                name = input('Alias: ')
                serv[name] = re.sub(r'[\'\"]', '', path)
        except:
            config.create(serv)
    else:
        for serv in p.__params__[1:]:
            name, path = serv.split('=')
            serv[name] = re.sub(r'[\'\"]', '', path)
        config.create(serv)
    print('\nConfig file creato')
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
    Core(instructions, verbose=['-v', '--verbose'] in p, interactive=not '-y' in p)
elif 'configure' in p:  # configura i servizi
    get_config()
else:
    Core([i for i in p.__params__], verbose=['-v', '--verbose'] in p, interactive=not '-y' in p)

#TODO parte di docker
