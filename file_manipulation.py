from utils import is_valid_file, call_process


class Filex:
    def __init__(self) -> None:
        pass

    def get_diff(self, path_file_a: str, path_file_b: str) -> list[str] | None:
        """
        controlla e restituisce la differenza fra due file
        :param path_file_a: file A
        :param path_file_b: file B
        :return: la differenza fra i due file
        """
        if not is_valid_file(path_file_a) or not is_valid_file(path_file_b):
            return None
        stdout, stderr = call_process('diff', [path_file_a, path_file_b])
        old: list = []
        new: list = []
        for line in stdout.split('\n'):
            if line.startswith('<'):
                old.append(line[1:].strip())
            elif line.startswith('>'):
                new.append(line[1:].strip())

        return ['\n'.join(old), '\n'.join(new)]

