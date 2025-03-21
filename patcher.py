#!/usr/bin/python3

from argparse import ArgumentParser
from os import getcwd, access as permissions, R_OK, W_OK, listdir
from os.path import join, isfile, exists, basename, abspath, dirname, isdir
from subprocess import call, Popen, PIPE
from logging import getLogger
from string import printable
from json import dumps, loads

current_dir: str = getcwd() + '/'
tab_char = '\t'
new_line = '\n'
VERSION: str = 'legacy'
PATCHER_LOGGER = getLogger('patcher')
COMPOSE_NAMES = ['compose.yml', 'compose.yaml', 'docker-compose.yaml', 'docker-compose.yml']

# Stampa i crediti e la versione
def print_credit() -> None:
    print(f'''
             _       _               
            | |     | |              
 _ __   __ _| |_ ___| |__   ___ _ __ 
| '_ \ / _` | __/ __| '_ \ / _ \ '__|
| |_) | (_| | || (__| | | |  __/ |   
| .__/ \__,_|\__\___|_| |_|\___|_|   
| |                                  
|_|                                  

legacy version (https://github.com/simonecocco/patcher)

made with ❤️ from simonecocco
    ''')

def find_dockerfile(generic_path):
    '''dato un path cerca un dockerfile'''

    global COMPOSE_NAMES

    if not isdir(generic_path):
        generic_path = dirname(generic_path)

    while True:
        try:
            generic_path_files = listdir(generic_path)
            if any((compose_name in generic_path_files for compose_name in COMPOSE_NAMES)):
                return generic_path
            else:
                generic_path = dirname(generic_path)
                if generic_path == '/': return None
        except:
            return None

def makefile_create(path: str) -> None:
    target: str = join(path, 'makefile') # percorso del makefile
    if not exists(target) or not isfile(target):
        # in caso esso non esista
        makefile = open(target, 'w')
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
    
def validate_path(path_to_validate, debug=False):
    '''
    Valida un path fornito.
    - path_to_validate prende una stringa (percorso)
    - dir_allowed prende un bool
    ritorna True se il path è ok
    '''

    global PATCHER_LOGGER

    if path_to_validate is None or not exists(path_to_validate):
        if debug: PATCHER_LOGGER.debug('incorrect path')
        return False
    
    permission_allowed = permissions(path_to_validate, R_OK) and permissions(path_to_validate, W_OK)
    if debug: PATCHER_LOGGER.debug(f'permission on {path_to_validate} is {"OK" if permission_allowed else "NOT OK"}')
    return permission_allowed

def semplificate_list(a_b_list):
    '''
    semplifica una lista dove i numeri potrebbero esser sequenziali
    creando una lista con una tupla che indica dove iniziano e dove finiscono
    '''
    if a_b_list is None or a_b_list == []: return []
    if len(a_b_list) == 1: return [(a_b_list[0], a_b_list[0])]

    new_list = []

    start_num = -1
    end_num = -1
    for index in range(len(a_b_list)-1):
        current_num = a_b_list[index]
        next_num = a_b_list[index+1]

        if start_num == -1:
            start_num = current_num
            end_num = current_num

        if  next_num == end_num + 1:
            end_num = next_num
        else:
            new_list.append((start_num, end_num))
            start_num = -1
            end_num = -1

    new_list.append((start_num, end_num))
    return new_list

def get_differences(bytes1, bytes2):
    ''''
    Controlla le differenze fra content1 e content2 e
    ritorna una lista con gli indici dei caratteri di A e di B differenti
    '''
    indexesA = []
    indexesB = []

    lenA = len(bytes1)
    lenB = len(bytes2)
    len_max = max(lenA, lenB)
    for general_index in range(len_max):
        current_byte_a = bytes1[general_index] if general_index < lenA else None
        current_byte_b = bytes2[general_index] if general_index < lenB else None

        # se non vi son più byte disponibili in A
        if current_byte_a is None:
            indexesB.append(general_index)
            continue

        # se non vi son più byte disponibili in B
        if current_byte_b is None:
            indexesA.append(general_index)
            continue

        if current_byte_a != current_byte_b:
            indexesA.append(general_index)
            indexesB.append(general_index)

    return semplificate_list(indexesA), semplificate_list(indexesB)

def print_diff_screen(title1, bytes1, title2, bytes2, sep_len=60):
    '''
    stampa una schermata con le differenze fra due contenuti
    - title1 stringa che descrive brevemente
    - bytes1 bytes da confrontare
    - title2 stringa che descrive brevemente
    - bytes2 bytes da confrontare
    stampa direttamente la view
    '''
    def print_header(separator, title):
        print(f'{separator}\nVista su {title}')

    def hexify(b):
        printable_codes = [hex(ord(c))[2:] for c in printable]
        hex_string = b.hex()
        hex_list = []
        chr_list = []
        for high, low in zip(hex_string[::2], hex_string[1::2]):
            hex_list.append(f'0x{high}{low}')
            chr_list.append(chr(int(f'{high}{low}', 16)) if f'{high}{low}' in printable_codes else '.')
        return hex_list, chr_list

    def print_diff(content, indexes_list, offset=10, print_len=8):
        content_len = len(content)
        content_edits = []
        for index_pair in indexes_list:
            start_index, end_index = index_pair
            end_index += 1
            start_index = start_index-offset if start_index-offset > 0 else 0
            end_index = end_index+offset if end_index+offset < content_len else content_len

            tmp_content = content[start_index:end_index]
            header = f'\n({start_index}-{end_index})'
            print(f'{header} ', end='')
            header = ' ' * (len(header)-1)
            hex_list, chr_list = hexify(tmp_content)
            module = len(hex_list) % print_len
            times = len(hex_list) // print_len
            for t in range(times):
                print(' '.join(hex_list[t*print_len:(t+1)*print_len]), ''.join(chr_list[t*print_len:(t+1)*print_len]))
                print(f'{header} ', end='')

            if module != 0:
                print(' '.join(hex_list[-module:] + ['    '] * (print_len - module)), ''.join(chr_list[-module:]))

            real_start_index = index_pair[0]
            real_end_index = index_pair[1]+1
            content_edits.append((real_start_index, real_end_index, content[real_start_index:real_end_index].hex()))
        return content_edits

    separator_start_end = '#' * sep_len
    indexes_bytes1, indexes_bytes2 = get_differences(bytes1, bytes2)
    edits_dict = {}
    print_header(separator_start_end, title1)
    edits_dict['A'] = print_diff(bytes1, indexes_bytes1)
    print_header('-' * sep_len, title2)
    edits_dict['B'] = print_diff(bytes2, indexes_bytes2)
    print(separator_start_end)

    return edits_dict

def first_backup(path, debug=False):
    '''esegue un backup del file alla sua versione originale'''
    path = abspath(path) # prendo la dir assoluta
    backup_path = join(dirname(path), f'.{basename(path)}.original')
    if exists(backup_path):
        if debug: PATCHER_LOGGER.debug(f'{backup_path} esiste già')
        return

    if debug: PATCHER_LOGGER.debug(f'eseguo primo backup del file {path} in {backup_path}')
    call(['cp', path, backup_path])

def get_patch_file_path(path):
    return join(dirname(path), f'.{basename(path)}.json')

def edit_bytes(bytes_content, editA, editB):
    bytes_content = [b for b in bytes_content]
    for edit in editA:
        bytes_content[edit[0]:edit[1]] = [-1] * (edit[1]-edit[0])
    for edit in editB:
        bytes_content[edit[0]:edit[1]] = [int(f'{high}{low}', 16) for high, low in zip(edit[2][::2], edit[2][1::2])]

    return b''.join(i.to_bytes(1) for i in bytes_content if i != -1)

def compute_edits(path_orig, edit_list):
    with open(path_orig, 'rb') as dest_file:
        content = dest_file.read()

    with open(path_orig, 'wb') as dest_file:
        dest_file.write(edit_bytes(content, edit_list['A'], edit_list['B']))

def compute_restore(path_orig, edits_list_of_list):
    with open(path_orig, 'rb') as dest_file:
        content = dest_file.read()

    print(edits_list_of_list)
    for dictAB in edits_list_of_list[::-1]:
        print(content, dictAB)
        content = edit_bytes(content, dictAB['B'], dictAB['A'])
        print(content)

    return content

def apply_patch(path_orig: str, path_new_file: str, backup: bool=True, docker_build: bool=True, hard_build: bool=False, debug=False) -> str:
    print(f'patching {path_orig} con {path_new_file}')
    assert validate_path(path_new_file, debug), f'{path_new_file} non è un percorso valido'
    assert validate_path(path_orig, debug), f'{path_orig} non è un percorso valido'

    path_orig = abspath(path_orig)
    path_new_file = abspath(path_new_file)

    if backup: first_backup(path_orig, debug)

    with open(path_orig, 'rb') as origin_file:
        original_file_bytes = origin_file.read()

    with open(path_new_file, 'rb') as new_file:
        new_file_bytes = new_file.read()

    edit_list = print_diff_screen(path_orig, original_file_bytes, path_new_file, new_file_bytes)
    risp: str = str(input(f"sei sicuro di voler applicare la patch? (y/n) \n")).strip()
    if not ('y' in risp) and not('Y' in risp):
        print('Patch non applicata')
        return
    
    if exists(get_patch_file_path(path_orig)):
        with open(get_patch_file_path(path_orig), 'r') as patch_file:
            patch_file_content = loads(patch_file.read())
    else:
        patch_file_content = []

    with open(get_patch_file_path(path_orig), 'w') as patch_file:
        patch_file_content.append(edit_list)
        patch_file.write(dumps(patch_file_content))

    compute_edits(path_orig, edit_list)
    makefile_path = find_dockerfile(path_orig)
    if makefile_path is not None:
        makefile_create(makefile_path)
        if docker_build and not hard_build:
            PATCHER_LOGGER.debug('docker build normale')
            call(['make', '-C', makefile_path])
        elif docker_build and hard_build:
            PATCHER_LOGGER.debug('docker build completa')
            call(['make', 'hard', '-C', makefile_path])
    elif debug:
        PATCHER_LOGGER.debug('makefile non trovato')

    print('Patch applicata correttamente')

# torna indietro con le versioni
def back2version(path: str, version: int, backup: bool=True, docker_build: bool=True, hard_build: bool=False, debug=False) -> str:
    path = abspath(path)
    assert validate_path(path), f'{path} inesistente!'
    assert exists(get_patch_file_path(path)), 'il file è alla sua prima versione'

    with open(get_patch_file_path(path), 'r') as patch_file:
        patch_list = loads(patch_file.read())

    assert version > -1 and version < len(patch_list), 'versione fuori dal range massimo'

    with open(path, 'rb') as path_content:
        content_of_path = path_content.read()

    edit_list = patch_list[version:]
    restored_content = compute_restore(path, edit_list)
    print(content_of_path, restored_content)
    
    print_diff_screen(f'{path} ATTUALE', content_of_path, f'{path} VERSIONE {version}', restored_content)
    
    risp: str = str(input(f"sei sicuro di voler tornare indietro? (y/n) ")).strip()
    if not ('y' in risp) and not('Y' in risp):
        print('Patch non applicata')
        return
    
    with open(path, 'wb') as origin_file:
        origin_file.write(restored_content)

    makefile_path = find_dockerfile(path)
    if makefile_path is not None:
        makefile_create(makefile_path)
        if docker_build and not hard_build:
            PATCHER_LOGGER.debug('docker build normale')
            call(['make', '-C', makefile_path])
        elif docker_build and hard_build:
            PATCHER_LOGGER.debug('docker build completa')
            call(['make', 'hard', '-C', makefile_path])
    elif debug:
        PATCHER_LOGGER.debug('makefile non trovato')
    print('Restore completed')
        
def main():
    aparse = ArgumentParser(prog='patcher', description='gestore delle patch per attacco e difesa')
    aparse.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False, help='non stampa i crediti')
    aparse.add_argument(
        '--no-bkp', '--no-backup', action='store_false', dest='recover_backup', default=True,
        help='non fa il backup del file che si va a sostituire'
    ) # '--no-bkp' not in sys.argv
    aparse.add_argument(
        '--no-docker', action='store_false', dest='docker_build', default=True,
        help='non fa il build del container'
    ) # '--no-docker' not in sys.argv
    aparse.add_argument(
        '-H', '--hard-build', action='store_true', dest='hard_build', default=False,
        help='esegue un docker-compose down e poi up. Non funziona se --no-docker è presente'
    ) # '--hard-build' in sys.argv
    aparse.add_argument(
        '-b', '--back', action='store_true', dest='restore', default=False,
        help='al posto di applicare la patch, torna una versione indietro per tutti i file (può essere usato solo con opzione file)'
    ) # '--back' in sys.argv or '-b' in sys.argv
    aparse.add_argument('--debug', action='store_true', default=False, dest='debug')
    aparse.add_argument(
        'action', required=True, dest='action', choices=['apply', 'a', 'back', 'b'], type=str, nargs=1,
        help='[apply a] [path del vecchio file] [path del file]\n[back b] [path del file] [numero versione]'
    )
    aparse.add_argument('action args', type=list, nargs='?', required=True, dest='action_args')

    args = aparse.parse_args()

    if not args.quiet:
        print_credit()

    # apply -> apply_patch(first_arg, second_arg, docker_build=docker_build, hard_build=hard_build, backup=recover_backup)
    # back -> back2version(first_arg, int(second_arg), backup=recover_backup, docker_build=docker_build, hard_build=hard_build)

    if args.action == 'apply' or args.action == 'a':
        apply_patch(args.action_args[0], args.action_args[1], args.backup, args.docker_build, args.hard_build, args.debug)
    elif args.action == 'back' or args.action == 'b':
        back2version(args.action_args[0], int(args.action_args[1]), args.backup, args.docker_build, args.hard_build, args.debug)

if __name__ == '__main__':
    main()
