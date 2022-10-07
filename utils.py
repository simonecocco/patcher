import os
from subprocess import call, Popen, PIPE


def is_valid_file(file_path: str, is_file: bool=True, readable: bool=True):
    """
    controlla se il file è valido
    :param file_path: path del file da controllare
    :param is_file: True per verificare che sia un file
    :param readable: True per verificare che sia leggibile
    :return: ritorna True se soddisfa le condizioni specificate (e soprattutto che esista)
    """
    exist: bool = os.path.exists(file_path)
    type: bool = not is_file or os.path.isfile(file_path) if exist else False
    can_read: bool = not is_file or not readable or open(file_path, 'r').readable() if exist else False
    return type and can_read


def call_process(cmd: str, params: list[str]=[]) -> list[str]:
    """
    chiama un processo
    :param cmd: chiamata
    :param params:
    :return: stdout, stderr
    """
    _process: Popen = Popen([cmd] + params, stdout=PIPE, stderr=PIPE)
    _stdout, _stderr = _process.communicate()
    return [_stdout.decode('utf-8'), _stderr.decode('utf-8')]