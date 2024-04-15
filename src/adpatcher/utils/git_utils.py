from adpatcher.utils.process_utils import call_process

GIT_MASTER_BRANCH_NAME: str = 'master'
GIT_ORIGINAL_BRANCH_NAME: str = 'original'

def git_config(username: str='Patcher', email: str='patcher@localhost') -> None:
    """
    Configura git
    :param username: nome utente
    :param email: email
    """
    call_process('git', ['config', 'user.name', username])
    call_process('git', ['config', 'user.email', email])

def set_main_git_branch_name() -> None:
    call_process('git', ['branch', '-M', GIT_MASTER_BRANCH_NAME])

def create_copy_of_original_service() -> None:
    call_process('git', ['add', '-A'])
    call_process('git', ['commit', '-a', '-m', 'Original service'])
    call_process('git', ['branch', '-C', GIT_MASTER_BRANCH_NAME, GIT_ORIGINAL_BRANCH_NAME])
    call_process('git', ['checkout', GIT_MASTER_BRANCH_NAME])

def create_new_git_branch(branch_name: str, checkout: bool=True) -> None:
    call_process('git', ['branch', '-C', 'master', branch_name])
    if checkout:
        call_process('git', ['checkout', branch_name])

def git_update_file() -> None:
    call_process('git', ['add', '--update'])

def git_commit(message: str='Bug fixing') -> None:
    # TODO aggiungi LLM che si metta a generare un messaggio di commit
    call_process('git', ['commit', '-a', '-m', message])

def git_rollback(how_many) -> None:
    call_process('git', ['reset', '--hard', f'HEAD~{how_many}'])

def git_save_stash() -> None:
    call_process('git', ['stash', 'save'])

def git_apply_stash() -> None:
    call_process('git', ['stash', 'apply'])

def git_change_branch(branch_name: str, ) -> None:
    git_save_stash()
    call_process('git', ['checkout', branch_name])
    git_apply_stash()

def git_merge_into_main_branch() -> None:
    call_process('git', ['merge', '-X', 'theirs', GIT_MASTER_BRANCH_NAME, 'quarantine', '--no-commit'])

def git_delete_branch(branch_name: str, force_deletion_of_branch: bool=False) -> None:
    call_process('git', ['branch', '-d' if not force_deletion_of_branch else '-D', branch_name])