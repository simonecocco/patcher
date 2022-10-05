#!/usr/bin/python3

from params import Params
import credits
from file_manipulation import Filex
import log
import utils
from makefile import Makefile

from os import getcwd, path
from sys import exit

'''
tab_char = '\t'
new_line = '\n'


# controlla che il path sia a posto
def validate(path: str, dir_allowed: bool = True) -> bool:
    if os.path.exists(path):
        if os.path.isfile(path) or dir_allowed:
            if not os.access(path, os.R_OK) or not os.access(path, os.W_OK):
                call(['sudo', 'chmod', '-R', '777', path])
                print(f"{path} is a {'file' if os.path.isfile(path) else 'dir'}")
                return True
        else:
            print(Fore.RED + f'{path} is a directory' + Fore.RESET)
            sys.exit(1)
            return False
    else:
        print(Fore.RED + f'{path} not exist' + Fore.RESET)
        sys.exit(1)
        return False

def dir_safe(dirpath: str, filepath: str) -> str:
    validate(dirpath, dir_allowed=True)
    if os.path.isdir(dirpath):
        dirpath = os.path.join(dirpath, os.path.basename(filepath))
        validate(dirpath, dir_allowed=False)
        return dirpath
    else:
        return dirpath

# torna indietro con le versioni
def back2version(path: str, version: int, backup: bool = True, docker_build: bool = True,
                 hard_build: bool = False) -> str:
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
    if not ('y' in risp) and not ('Y' in risp):
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
def parse_file(path: str, docker_build: bool = True, hard_build: bool = False, backup: bool = True,
               restore: bool = False) -> None:
    validate(path, dir_allowed=False)
    print(f'leggo da {path}')

    patch = open(path, 'r')
    paths: list[str] = patch.readlines()
    last_makefile_path: str | None = None

    for patch_path in paths:
        patch_path = patch_path.strip()
        if len(patch_path) <= 1 and docker_build and (last_makefile_path is not None):
            if hard_build:
                print(
                    Fore.YELLOW + f"hard reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', 'hard', '-C', last_makefile_path])
            else:
                print(
                    Fore.YELLOW + f"reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
                call(['make', '-C', last_makefile_path])
            last_makefile_path = None
        elif len(patch_path) > 2:
            try:
                path_orig, path_new_file = re.findall('^([\/\S\s]{1,})\s([\S\s]{1,})$', patch_path)[0]
                if not restore:
                    print(Fore.YELLOW + f'{path_orig} -> {path_new_file}' + Fore.RESET)
                    last_makefile_path = apply_patch(path_orig, path_new_file, docker_build=False, quiet=True,
                                                     backup=backup)
                else:
                    print(Fore.YELLOW + f'{path_orig}' + Fore.RESET)
                    last_makefile_path = back2version(dir_safe(path_orig, path_new_file), -1, backup=backup,
                                                      docker_build=False)
            except:
                print(f'{path_orig} non applicata')
    if docker_build and (last_makefile_path is not None):
        if hard_build:
            print(
                Fore.YELLOW + f"hard reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
            call(['make', 'hard', '-C', last_makefile_path])
        else:
            print(
                Fore.YELLOW + f"reboot per il container {'/'.join(last_makefile_path.split('/')[:-1])}\n" + Fore.RESET)
            call(['make', '-C', last_makefile_path])
        last_makefile_path = None
'''


def back2version(mkf: Makefile | None, file_path: str, version: int = -1, docker_build: bool = True, hard_build: bool = True) -> None
    pass # todo


def apply_patch(mkf: Makefile | None, old_path_file: str, new_path_file: str, do_backup: bool = True, docker_build: bool = True, hard_build: bool = True) -> None:
    """
    todo
    :param mkf:
    :param old_path_file:
    :param new_path_file:
    :param do_backup:
    :param docker_build:
    :param hard_build:
    :return:
    """
    if not utils.is_valid_file(old_path_file):
        log.error(f'Path non valido {old_path_file}')
        exit(-1)
    if not utils.is_valid_file(old_path_file):
        log.error(f'Path non valido {new_path_file}')
        exit(-1)

    if do_backup:
        log.output(f'Eseguo il backup di {old_path_file} a {Filex.backup_file(old_path_file)}')

    log.output(f'Sostituisco {old_path_file} con {new_path_file}')
    Filex.overwrite_file(old_path_file, new_path_file, old_file_backup=False)

    if mkf is not None and docker_build and hard_build:
        log.output('Docker hard build', ec=True)
        mkf.docker_hardreboot()
    elif mkf is not None and docker_build and not hard_build:
        log.output('Docker soft build', ec=True)
        mkf.docker_softreboot()

    log.output('Completato')


current_dir: str = getcwd() + '/'

# MAIN
if __name__ == '__main__':
    p: Params = Params(min_len=1, help_function=credits.print_help)  # gestione dei parametri
    if not p.check(['-q', '--quiet']):  # [-q, --quiet] dice al programma di non stampare i crediti
        credits.print_credit()
    if p.check(['-h', '--help']):  # [-h, --help] mostra l'aiuto
        credits.print_help()

    recover_backup: bool = not p.check('--no-bkp')
    docker_build: bool = not p.check('--no-docker')
    hard_build: bool = p.check('--hard-build')
    restore: bool = p.check(['--back', '-b'])
    preserve_patch: bool = p.check(['--preserve-patch', '-p'])  # con questa opzione attiva le patch non verranno cancellate ma rimarrà sempre il file

    first_arg: str = p.get_if(1, len(p) > 1, '')  # opzionale: solo per percorsi differenti dal path
    second_arg: str = p.get_if(2, not p.check(['f', 'file', 'gui', 'history']), '')

    makefile: Makefile | None
    if first_arg != '':
        makefile_target: str = path.join(first_arg.replace(current_dir, '').split('/')[0], 'makefile')
        makefile = Makefile(makefile_target)

    action: list[list[str]] = [['apply', 'a'], ['back', 'b'], ['file', 'f'], ['gui'], ['history']]
    linked_function: list = [
        #lambda: apply_patch(first_arg, second_arg, docker_build=docker_build, hard_build=hard_build,
        #                    backup=recover_backup),
        #lambda: back2version(first_arg, int(second_arg), backup=recover_backup, docker_build=docker_build,
        #                     hard_build=hard_build),
        #lambda: parse_file(first_arg, docker_build=docker_build, hard_build=hard_build, backup=recover_backup,
        #                   restore=restore),
        lambda: apply_patch(makefile, first_arg, second_arg, recover_backup, docker_build, hard_build),
        lambda: print('ciao2'),
        lambda: print('ciao3'),
        lambda: print('ciao4'),
        lambda: print('ciao5')
    ]
    p.action_param(0, action, linked_function)
