from adpatcher.makefile import Makefile
from adpatcher.utils.file_utils import is_valid_file
from adpatcher.utils.stdout_utils import warning
from adpatcher.utils.git_utils import *

class Service:
    __slots__: list = [
        'abs_disk_path',
        'port',
        'name',
        'alias',
        'service_makefile',
        'vulnerable_file',
        'current_working_directory'
    ]

    def __init__(self, abs_disk_path: str, port: tuple, name: str, alias: str, vulnerable_file: str='UNKNOWN', dockerv2: bool=False, verbose: bool=False):
        self.abs_disk_path: str = abs_disk_path
        self.port: tuple = port
        self.name: str = name
        self.alias: str = alias
        self.service_makefile: Makefile(self.abs_disk_path, docker_v2=dockerv2, verbose=verbose)
        self.vulnerable_file: str = vulnerable_file
        self.current_working_directory: str = os.getcwd()
        with self:
            git_config()
            set_main_git_branch_name()
            create_copy_of_original_service()


    def __dict__(self):
        return {
            'disk_path': self.abs_disk_path,
            'port': self.port,
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

    def apply_patch(self, patches_to_apply_list: list, atomic: bool=False) -> bool:
        if self.vulnerable_file == 'UNKNOWN':
            self.create_quarantine_zone()
            self.vulnerable_file = patches_to_apply_list
        with self:
            for patch_to_apply in patches_to_apply_list:
                original_file_path, new_file_path = patch_to_apply
                if not is_valid_file(original_file_path) or not is_valid_file(new_file_path):
                    warning(f'Original file path: {original_file_path} or new file path: {new_file_path} is not valid.')
                    if atomic:
                        return False
                call_process('rm', [original_file_path])
                call_process('cp', [new_file_path, original_file_path])
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

    def close_quarantine() -> None:
        with self:
            git_merge_into_main_branch()
            not_merged_files: list = check_for_uncompleted_merges()
            if len(not_merged_files) > 0:
                solve_merge_conflicts()
            git_update_file()
            git_commit('Merged quarantine')
            git_change_branch(GIT_MASTER_BRANCH_NAME)
            self.vulnerable_file = 'UNKNOWN'
