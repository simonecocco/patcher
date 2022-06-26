#!/bin/bash python3

import sys
from colorama import Fore, Back, Style
import os
from subprocess import call, Popen, PIPE
import re

current_dir: str = os.getcwd() + '/'
tab_char = '\t'
new_line = '\n'
VERSION: str = '1.0'

# Stampa i crediti e la versione
def print_credit() -> None:
    print(Fore.BLUE + '''
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█▀▄▄▀█ ▄▄▀█▄ ▄█▀▄▀█ ████ ▄▄█ ▄▄▀
█ ▀▀ █ ▀▀ ██ ██ █▀█ ▄▄ █ ▄▄█ ▀▀▄
█ ████▄██▄██▄███▄██▄██▄█▄▄▄█▄█▄▄
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

    ''' + Fore.RESET)
    print(Fore.GREEN + 'made with ❤️ from d1dpvl' + Fore.RESET + f'\nVersione: {VERSION}\n')

# si assicura che il makefile esista
def makefile_check(path: str) -> None:
    target: str = os.path.join(path, 'makefile')
    if not os.path.exists(target) or not os.path.isfile(target):
        makefile = open(target, 'wb')
        makefile.write('all: build up\n')
        makefile.write('build:\n\tsudo docker-compose build\n')
        makefile.write('up:\n\tsudo docker-compose up --build -d\n')
        makefile.write('down:\n\tsudo docker-compose down\n')
        makefile.write('hard: build down up\n')
        makefile.close()

# Chiama un processo e ritorna il suo output
def call_process(cmd: list) -> list:
    process: Popen = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return [stdout.decode('utf-8'), stderr.decode('utf-8')]

# Stampa la guida
def print_help() -> None:
    print('''come usarlo:
    [apply a] [path del vecchio file] [path del file] OPZIONI
    [back b] [path del file] [numero versione] OPZIONI
    [file f] [file con le modifiche multiple] OPZIONI

    OPZIONI

    -q -> non stampa i crediti
    --no-bkp -> non fa il backup del file che si va a sostituire (solo con azione 'back')
    --no-docker -> non fa il build del container
    --hard-build -> esegue un docker-compose down e poi up. Non funziona se --no-docker è presente

    ''')
    sys.exit(0)

# controlla che il path sia a posto
def validate(path: str, dir_allowed: bool=True) -> bool:
    if os.path.exists(path):
        if os.path.isfile(path) or dir_allowed:
            if not os.access(path, os.R_OK) or not os.access(path, os.W_OK):
                call(['sudo', 'chmod', '-R', '777', path])
                return os.path.isfile(path)
        else:
            print(Fore.RED + f'{path} is a directory' + Fore.RESET)
            sys.exit(1)
            return False
    else:
        print(Fore.RED + f'{path} not exist' + Fore.RESET)
        sys.exit(1)
        return False


# mostra le differenze
def get_differences(path_old: str, path_new: str) -> str:
    stdout, stderr = call_process(['diff', path_old, path_new])
    old: list = []
    new: list = []
    for line in stdout.split('\n'):
        if line.startswith('<'):
            old.append(line)
        elif line.startswith('>'):
            new.append(line)
    return f"{Fore.CYAN}{path_old}:{new_line}{(tab_char+new_line).join(old)}{new_line*2}{Fore.GREEN}{path_new}:{new_line}{(tab_char+new_line).join(new)}{Fore.RESET}"

# esegue il backup del file
def backup_file(path: str) -> None:
    path_n: int = 0
    while os.path.exists(f'{path}.bkp{path_n}'):
        path_n += 1
    call(['cp', path, path+f'.bkp{path_n}'])
    print(f'new file {path}.bkp{path_n}')
    if not os.path.exists(f'{path}.bkp{path_n}'):
        print(f'Backup failed ({path})')
        sys.exit(1)
    print(Fore.YELLOW + f'Per tornare indietro usa\nback {path} {path_n}' + Fore.RESET)

# applica la patch
def apply_patch(path_orig: str, path_new_file: str, docker_build: bool=True, quiet: bool=False, hard_build: bool=False) -> str:
    print(f'patching {path_orig} with {path_new_file}')
    validate(path_new_file, dir_allowed=False) # le directory non son consentite
    if not validate(path_orig):
        path_orig = path_orig + os.path.basename(path_new_file) # se è una directory usa il nome del file nuovo
    diff: str = get_differences(path_orig, path_new_file)
    risp: str = str(input(f"sei sicuro di voler applicare la patch? (y/n)\nGuarda le modifiche:\n{diff}\n")).strip()
    if not ('y' in risp) and not('Y' in risp):
        print('Patch non applicata')
        sys.exit(1)
    backup_file(path_orig)
    call(['cp', path_new_file, path_orig])
    makefile_path: str = path_orig.replace(current_dir, '') if current_dir in path_orig else path_orig
    makefile_path = makefile_path.split('/')[0]
    makefile_check(makefile_path)
    if docker_build and not hard_build:
        call(['make', '-C', makefile_path])
    elif docker_build and hard_build:
        call(['make', 'hard', '-C', makefile_path])
    elif not quiet:
        print('Usa ' + Fore.YELLOW + 'make' + Fore.RESET + ' per applicare la patch')
    print('Patch applicata')
    return makefile_path

# torna indietro con le versioni
def back2version(path: str, version: int, backup: bool=True, docker_build: bool=True, hard_build: bool=False) -> str:
    path_n: int = 0
    while os.path.exists(f'{path}.bkp{path_n}'):
        path_n += 1
    print(f'Ultima versione: {path_n - 1}')
    target_version = path_n + version if version < 0 else version
    target_path: str = f'{path}.bkp{target_version}'
    if not os.path.exists(target_path):
        print(f'versione {target_version} inesistente ({target_path})')
        sys.exit(1)
    
    diff: str = get_differences(path, target_path)
    risp: str = str(input(f"sei sicuro di voler tornare indietro? (y/n)\nGuarda le modifiche:\n{diff}\n")).strip()
    if not ('y' in risp) and not('Y' in risp):
        print('Patch non applicata')
        sys.exit(1)
    if backup:
        call(['mv', path, f'{path}.bkp{path_n}'])
    call(['cp', target_path, path])
    makefile_path: str = path.replace(current_dir, '') if current_dir in path else path
    makefile_path = makefile_path.split('/')[0]
    makefile_check(makefile_path)
    if docker_build and not hard_build:
        call(['make', '-C', makefile_path])
    elif docker_build and hard_build:
        call(['make', 'hard', '-C', makefile_path])
    else:
        print('Usa ' + Fore.YELLOW + 'make' + Fore.RESET + ' per applicare la patch')
    print('Restore completed')
    return makefile_path

# applica molteplici patch
def parse_file(path: str, docker_build: bool=True, hard_build: bool=False) -> None:
    validate(path, dir_allowed=False)

    patch = open(path, 'r')
    paths: list[str] = patch.readlines()
    last_makefile_path: str | None = None
    for patch_path in paths:
        if len(patch_path) == 0 and docker_build and (last_makefile_path is not None):
            if hard_build:
                print(Fore.YELLOW + f"hard reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', 'hard', '-C', last_makefile_path])
            else:
                print(Fore.YELLOW + f"reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', '-C', last_makefile_path])
            last_makefile_path = None
        else:
            continue

        path_orig, path_new_file = re.findall('^([\/\S\s]{1,})\s([\S\s]{1,})$', patch_path)[0]
        print(Fore.YELLOW + '{path_orig} -> {path_new_file}' + Fore.RESET)
        last_makefile_path = apply_patch(path_orig, path_new_file, docker_build=False, quiet=True)
        
# main
if '-q' not in sys.argv:
    print_credit()
if len(sys.argv) < 4 or 'help' in sys.argv:
    print_help()

recover_backup: bool = '--no-bkp' not in sys.argv
docker_build: bool = '--no-docker' not in sys.argv
hard_build: bool = '--hard-build' not in sys.argv
action: str = sys.argv[1]
first_arg: str = sys.argv[2]
second_arg: str = sys.argv[3]

if action == 'apply' or action == 'a':
    apply_patch(first_arg, second_arg, docker_build=docker_build, hard_build=hard_build)
elif action == 'back' or action == 'b':
    back2version(first_arg, int(second_arg), backup=recover_backup, docker_build=docker_build, hard_build=hard_build)
elif action == 'file' or action == 'f':
    parse_file(first_arg, docker_build=docker_build, hard_build=hard_build) # todo
else:
    print_help()
