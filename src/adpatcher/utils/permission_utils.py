from os import geteuid, getgroups, stat

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
