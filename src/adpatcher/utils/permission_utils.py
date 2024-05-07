from os import geteuid, getgroups, stat
from getpass import getuser
from adpatcher.utils.process_utils import call_process

def is_root_user() -> bool:
    """
    controlla se l'utente è root
    :return: True se è root
    """
    return geteuid() == 0

def is_docker_user() -> bool:
    """
    Controlla se l'utente è aggiunto al gruppo docker
    """
    groups = getgroups()
    docker_group_id = stat('/var/run/docker.sock').st_gid
    return docker_group_id in groups

def add_user_to_docker() -> None:
    call_process('sudo', ['usermod', '-aG', 'docker', getuser()])