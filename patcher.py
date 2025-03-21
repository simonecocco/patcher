#!/usr/bin/python3

from argparse import ArgumentParser
from os import getcwd, access as permissions, R_OK, W_OK
from os.path import join, isfile, exists
from subprocess import call, Popen, PIPE
from logging import getLogger
from string import printable

current_dir: str = getcwd() + '/'
tab_char = '\t'
new_line = '\n'
VERSION: str = 'legacy'
PATCHER_LOGGER = getLogger('patcher')

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

# trova le differenze
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

def print_diff_screen(title1, bytes1, title2, bytes2):
    '''stampa una schermata con le differenze fra due contenuti'''
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

    sep_len = 60
    separator_start_end = '#' * sep_len
    indexes_bytes1, indexes_bytes2 = get_differences(bytes1, bytes2)
    print_header(separator_start_end, title1)
    print_diff(bytes1, indexes_bytes1)
    # ...
    print_header('-' * sep_len, title2)
    print_diff(bytes2, indexes_bytes2)
    # ...
    print(separator_start_end)

def dir_safe(dirpath: str, filepath: str) -> str:
    validate(dirpath, dir_allowed=True)
    if os.path.isdir(dirpath):
        dirpath = os.path.join(dirpath, os.path.basename(filepath))
        validate(dirpath, dir_allowed=False)
        return dirpath
    else:
        return dirpath

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
def apply_patch(path_orig: str, path_new_file: str, backup: bool=True, docker_build: bool=True, quiet: bool=False, hard_build: bool=False) -> str:
    print(f'patching {path_orig} with {path_new_file}')
    validate(path_new_file, dir_allowed=False)
    path_orig = dir_safe(path_orig, path_new_file)
    diff: str = get_differences(path_orig, path_new_file)
    risp: str = str(input(f"sei sicuro di voler applicare la patch? (y/n)\nGuarda le modifiche:\n{diff}\n")).strip()
    if not ('y' in risp) and not('Y' in risp):
        print('Patch non applicata')
        sys.exit(1)
    print(path_orig)
    backup_file(path_orig)
    call(['cp' if backup else 'mv', path_new_file, path_orig])
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
    call(['cp' if backup else 'mv', target_path, path])
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
def parse_file(path: str, docker_build: bool=True, hard_build: bool=False, backup: bool=True, restore: bool=False) -> None:
    validate(path, dir_allowed=False)
    print(f'leggo da {path}')

    patch = open(path, 'r')
    paths: list[str] = patch.readlines()
    last_makefile_path: str | None = None

    for patch_path in paths:
        patch_path = patch_path.strip()
        if len(patch_path) <= 1 and docker_build and (last_makefile_path is not None):
            if hard_build:
                print(Fore.YELLOW + f"hard reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', 'hard', '-C', last_makefile_path])
            else:
                print(Fore.YELLOW + f"reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', '-C', last_makefile_path])
            last_makefile_path = None
        elif len(patch_path) > 2:
            try:
                path_orig, path_new_file = re.findall('^([\/\S\s]{1,})\s([\S\s]{1,})$', patch_path)[0]
                if not restore:
                    print(Fore.YELLOW + f'{path_orig} -> {path_new_file}' + Fore.RESET)
                    last_makefile_path = apply_patch(path_orig, path_new_file, docker_build=False, quiet=True, backup=backup)
                else:
                    print(Fore.YELLOW + f'{path_orig}' + Fore.RESET)
                    last_makefile_path = back2version(dir_safe(path_orig, path_new_file), -1, backup=backup, docker_build=False)
            except:
                print(f'{path_orig} non applicata')
    if docker_build and (last_makefile_path is not None):
            if hard_build:
                print(Fore.YELLOW + f"hard reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', 'hard', '-C', last_makefile_path])
            else:
                print(Fore.YELLOW + f"reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', '-C', last_makefile_path])
            last_makefile_path = None
        
def configure_env(debug=False):
    pass #TODO

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
        'action', required=True, dest='action', choices=['apply', 'a', 'back', 'b', 'file', 'f'], type=str, nargs=1,
        help='[apply a] [path del vecchio file] [path del file]\n[back b] [path del file] [numero versione]\n[file f] [file con le modifiche multiple]'
    )
    aparse.add_argument('action args', type=list, nargs='?', required=True, dest='action_args')

    args = aparse.parse_args()

    if not args.quiet:
        print_credit()

    configure_env(debug=args.debug)

    # apply -> apply_patch(first_arg, second_arg, docker_build=docker_build, hard_build=hard_build, backup=recover_backup)
    # back -> back2version(first_arg, int(second_arg), backup=recover_backup, docker_build=docker_build, hard_build=hard_build)
    # file -> parse_file(first_arg, docker_build=docker_build, hard_build=hard_build, backup=recover_backup, restore=restore)

if __name__ == '__main__':
    main()
