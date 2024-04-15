from os import geteuid

def is_root_user() -> bool:
    """
    controlla se l'utente è root
    :return: True se è root
    """
    return geteuid() == 0