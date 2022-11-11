from config import read
import log
from os import path
from utils import is_valid_file
from sys import exit

class Core:
    def __init__(self, instructions: list[str], verbose: bool = True, interactive: bool = True):
        self.instructions: list[str] = instructions
        self.aliases: dict = read()
        self.verbose: bool = verbose
        self.interactive: bool = interactive
        self.__exec__(verbose, interactive)
        #todo

    def __restoredir__(self, dir: str, version: int, files_to_keep: list[str]) -> None:
        pass #TODO

    def __restoredir__(self, f: str, version: int) -> None:
        pass #TODO

    def __exec__(self) -> None:
        def solve_alias(name: str) -> str:
            res: str = name
            start: str = name.split('/')[0]
            if start in self.aliases.keys():
                res = path.join(self.aliases[start], '/'.join(name.split('/')[1:]))
            return res

        file_to_keep: list[str] = []
        file_to_patch: dict = {}
        file_to_restore: dict = {}

        for instruction in self.instructions:
            if '=' in instruction:
                origin_file, action = instruction.split('=')
                origin_file = solve_alias(origin_file)
                if not is_valid_file(origin_file, is_file=False):
                    print(f'{origin_file} non valido, annullo')
                    exit(-1)
                try:
                    file_to_restore[origin_file] = int(action)
                except:
                    file_to_patch[origin_file] = action
            else:
                file_to_keep.append(solve_alias(instruction))

        for old_file, version in file_to_restore:
            if path.isdir(old_file):
                pass #TODO
            else:
                pass #TODO


