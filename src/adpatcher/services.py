from tabnanny import verbose
from adpatcher.makefile import Makefile
from adpatcher.utils.file_utils import is_valid_file
from adpatcher.utils.stdout_utils import output, warning
from adpatcher.utils.git_utils import *
from adpatcher.utils.process_utils import call_process
from adpatcher.utils.diff_utils import call_diff
from colorama import Fore, Back, Style
from os import chdir, getcwd
from os.path import abspath, exists, join

class Service:
    __slots__: list = [
        'abs_disk_path',
        'port',
        'internal_port',
        'name',
        'alias',
        'service_makefile',
        'vulnerable_file',
        'current_working_directory',
        'protocol'
    ]

    def __init__(self, abs_disk_path: str, port: str, internal_port: str, protocol: str, name: str, alias: str, vulnerable_file: str='UNKNOWN', dockerv2: bool=False, verbose: bool=False):
        self.abs_disk_path: str = abs_disk_path
        try:
            external, internal = port.split('->', maxsplit=1)
            self.port: str = external.split(':')[-1]
            self.internal_port, self.protocol = internal.split('/')
        except :
            self.port: str = port
            self.internal_port: str = internal_port
            self.protocol: str = protocol
        self.name: str = name
        self.alias: str = alias
        self.service_makefile: Makefile = Makefile(self.abs_disk_path, docker_v2=dockerv2, verbose=verbose)
        self.vulnerable_file: str = vulnerable_file
        self.current_working_directory: str = getcwd()
        if not exists(join(self.abs_disk_path, '.git')):
            with self:
                git_config()
                set_main_git_branch_name()
                create_copy_of_original_service()


    def __dict__(self):
        return {
            'disk_path': self.abs_disk_path,
            'port': self.port,
            'internal_port': self.internal_port,
            'protocol': self.protocol,
            'name': self.name,
            'alias': self.alias,
            'makefile_path': self.service_makefile.service_mf_path,
            'vulnerable_file': self.vulnerable_file,
        }

    def __str__(self):
        return f"Service {self.name} ({self.alias}) at {self.abs_disk_path} with port {self.port}"

    def __repr__(self):
        return self.__str__()

    def analyze_service(self):
        raise NotImplementedError('Presto verrà implementato...')
        
    def __call__(self, action: str):
        self.service_makefile(action)

    def __enter__(self):
        chdir(self.abs_disk_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        chdir(self.current_working_directory)

    def create_quarantine_zone(self) -> None:
        with self:
            create_new_git_branch('quarantine')

    def apply_patch(self, patch_to_apply: tuple, assume_yes: bool=False) -> bool:
        return self.apply_list_of_patches([patch_to_apply], atomic=True, assume_yes=assume_yes)

    def apply_list_of_patches(self, patches_to_apply_list: list, atomic: bool=False, assume_yes: bool=False) -> bool:
        if self.vulnerable_file == 'UNKNOWN':
            self.create_quarantine_zone()
            self.vulnerable_file = patches_to_apply_list[0] # TODO
        for patch_to_apply in patches_to_apply_list:
            original_file_path, new_file_path = patch_to_apply
            new_file_path = abspath(new_file_path)
            if not is_valid_file(original_file_path) or not is_valid_file(new_file_path):
                warning(f'Original file path: {original_file_path} or new file path: {new_file_path} is not valid.')
                if atomic:
                    return False
            if not assume_yes:
                call_diff(original_file_path, new_file_path)
                warning('Confirm? [Y/n] ')
                resp: str = input()
                if resp != 'Y':
                    warning(f'Cancelled the patching of {original_file_path}')
                    if atomic:
                        return False
            with self:
                output(f'Replacing {original_file_path} with {new_file_path}', verbose=verbose)
                call_process('rm', [original_file_path])
                call_process('cp', [new_file_path, original_file_path])
        with self:
            git_update_file()
            git_commit()
            return True

    def __sub__(self, version: int) -> None:
        with self:
            git_rollback(version)

    def sos(self) -> None:
        with self:
            git_change_branch(GIT_ORIGINAL_BRANCH_NAME)
            self.service_makefile('build')
            self.service_makefile('up')
            git_change_branch('quarantine')

    def close_quarantine(self) -> None:
        with self:
            git_change_branch(GIT_MASTER_BRANCH_NAME)
            git_merge_into_main_branch()
            git_commit('Closed quarantine')
            git_delete_branch('quarantine')

    def pretty_print(self):
        print(f'{Fore.GREEN if self.vulnerable_file == "UNKNOWN" else Fore.RED}{self.name} ({self.alias}) at {self.abs_disk_path} with port {self.port}{Style.RESET_ALL}')

    def tarball(self, tarball_directory_output: str) -> None:
        call_process('tar', ['-czvf', f'{tarball_directory_output}/{self.name}.tar.gz', self.abs_disk_path])