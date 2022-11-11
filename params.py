from sys import argv, exit
EXIT_NO_ARGS: int = 65

class Params:
    def __init__(self, help_description: str = '', call_help_if_zero: bool = True, help_options: list[str] = ['-h', '--help']) -> None:
        self.__params__: list[str] = argv[1:].copy()
        self.__help__: str = help_description
        if len(self.__params__) == 0:
            if call_help_if_zero:
                self.help(exit_after=False)
            exit(EXIT_NO_ARGS)
        for opt in help_options:
            if opt in self.__params__:
                self.help()

        

    def help(self, exit_after: bool = True) -> None:
        if self.__help__ == '':
            print('Help not avaiable')
            exit(-1)
        print(self.__help__)
        if exit_after:
            exit(0)

    def __getitem__(self, key: str | int | list) -> str | None:
        if type(key) is int:
            return self.__params__[key]
        elif type(key) is str:
            flag: bool = False
            for p in self.__params__:
                if key == p and not flag:
                    flag = True
                elif flag:
                    return p
            return None
        elif type(key) is list:
            for k in key:
                if (tmp:=self[k]) is not None:
                    return tmp
            else:
                return None
        else:
            raise Exception(f'{type(key)} not supported')

    def __len__(self) -> int:
        return len(self.__params__)

    def __contains__(self, key: str | list) -> bool:
        if type(key) is str:
            return key in self.__params__
        else:
            for x in key:
                if x in self.__params__:
                    return True

            return False
