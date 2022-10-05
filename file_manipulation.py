from utils import is_valid_file, call_process


class Filex:
    def __init__(self) -> None:
        pass

    @staticmethod
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

    @staticmethod
    def overwrite_file(old_path_file: str, new_path_file: str, old_file_backup: bool = True) -> bool:
        """
        Sosituisce il vecchio file con uno nuovo e fa il backup del vecchio.
        :param old_path_file: path del vecchio file da sovrascrivere
        :param new_path_file: percorso del nuovo file che andrà a sovrascrivere il vecchio
        :return True se il file ed il backup sono andati bene
        """
        pass #todo

    @staticmethod
    def backup_file(file_path: str) -> str | None:
        """
        Esegue il backup del file fornito
        :param file_path percorso del file su cui fare il backup
        :return stringa con il percorso del file fatto a backup, None nel caso il backup non venga fatto
        """
        pass #todo

    @staticmethod
    def restore_file(file_path: str, version: int) -> bool:
        pass
