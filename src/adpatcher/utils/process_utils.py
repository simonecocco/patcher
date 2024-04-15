from subprocess import Popen, PIPE

def call_process(cmd: str, params: list=[]) -> list:
    """
    chiama un processo
    :param cmd: chiamata
    :param params:
    :return: stdout, stderr
    """
    _process: Popen = Popen([cmd] + params, stdout=PIPE, stderr=PIPE)
    _stdout, _stderr = _process.communicate()
    return [_stdout.decode('utf-8'), _stderr.decode('utf-8')]