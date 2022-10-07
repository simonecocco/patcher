from atexit import register
from utils import is_valid_file, call_process
import log


class Filex:
    def __init__(self) -> None:
        pass

    @staticmethod
    def __editregister__(register_file_name: str, version: int | None = None) -> int:
        """
        scrive il registro delle modifiche del file
        :param file_path path del file da modificare
        :param version versione del file da ripristinare, usare None per eseguire solo il backup
        :return la versione del file
        """
        file_register = None
        n_version: int
        try:
            file_register = open(register_file_name, 'r+')
        except Exception:
            file_register = open(register_file_name, 'w')
            file_register.write('0')
            file_register.close()
            del file_register
            return 0
            
        if version is None:
            n_version = int(file_register.read()) + 1
            file_register.seek(0, 0)
            file_register.write(str(n_version))
            file_register.close()
            del file_register
            return n_version
        else:
            n_version = int(file_register.read())
            n_version = list(range(n_version + 1))[version]
            file_register.seek(0, 0)
            file_register.write(n_version)
            file_register.close()
            del file_register
            return n_version

    @staticmethod
    def get_diff(path_file_a: str, path_file_b: str) -> list[str] | None:
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

        return ['\n'.join(old), '\n'.join(new)] if len(old) > 0 or len(new) > 0 else None

    @staticmethod
    def overwrite_file(old_path_file: str, new_path_file: str, old_file_backup: bool = True, preserve_new_file: bool = False) -> bool:
        """
        Sosituisce il vecchio file con uno nuovo e fa il backup del vecchio.
        :param old_path_file: path del vecchio file da sovrascrivere
        :param new_path_file: percorso del nuovo file che andrà a sovrascrivere il vecchio
        :return True se il file ed il backup sono andati bene
        """
        if old_file_backup:
            Filex.backup_file(old_path_file)
        print(old_path_file, new_path_file)
        Filex.__errorcheck__(*call_process('mv' if not preserve_new_file else 'cp', [new_path_file, old_path_file]), verbose=True)

    @staticmethod
    def __errorcheck__(stdout, stderr, verbose: bool = False) -> bool:
        """
        :param stdout output del comando
        :param stderr errori del comando
        :param verbose deve mostrare output?
        :return True se ci sono errori
        """
        tmp: bool
        if (tmp := len(stderr) > 0) and verbose:
            log.error(f'Error: {stdout}, {stderr}')
        return tmp

    @staticmethod
    def backup_file(file_path: str) -> str | None:
        """
        Esegue il backup del file fornito
        :param file_path percorso del file su cui fare il backup
        :return stringa con il percorso del file fatto a backup, None nel caso il backup non venga fatto
        """
        only_file_name: str = file_path.split('/')[-1]
        prec_dir: str = '/'.join(file_path.split('/')[:-1])
        bkp_dir: str = f'{prec_dir}/.bkp_{only_file_name}'
        Filex.__errorcheck__(*call_process('mkdir', [bkp_dir]))
        file_version: int = Filex.__editregister__(f'{bkp_dir}/register', None)
        if Filex.__errorcheck__(*call_process('cp', [file_path, file_backup_path := f'{bkp_dir}/{only_file_name}{file_version}']), verbose=True):
            exit(-1)
        print(file_backup_path)
        return file_backup_path

    @staticmethod
    def restore_file(file_path: str, version: int) -> bool:
        pass
