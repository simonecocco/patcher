from sys import argv, exit


class Params:
    """
    copia la lista dei parametri, infatti la lista copiata serve ad
    apportare modifiche
    """

    def __init__(self, min_len: int=-1, help_function=None) -> None:
        """
        costruttore della classe
        :param min_len: minimo di argomenti presenti per evitare che venga chiamato l'help
        :param help_function: puntatore alla funzione di help
        """
        self.__params__: list[str] = argv.copy()[1:]
        self.__help_fn__ = help_function
        if 0 < min_len > len(self.__params__):
            if help_function is not None:
                help_function()
            else:
                print('Argomenti insufficienti!')
                exit(-1)

    def remove(self, param: str) -> bool:
        """
        controlla se un determinato parametro è stato passato, se la condizione è vera
        allora lo rimuove dalla lista.
        :param param: parametro da controllare se è presente
        :return: True se il parametro è stato trovato nella lista
        """
        if param in self.__params__:
            self.__params__.remove(param)
            return True
        else:
            return False

    def action_param(self, index: int, list_params: list, list_actions: list) -> None:
        """
        controlla il parametro dato in quel determinato indice
        a seconda di quale parametro è indicato, viene eseguita una diversa funzione
        :param index: indice del parametro da controllare
        :param list_params: lista delle opzioni possibili
        :param list_actions: a seconda dell'opzione passata come parametro chiama l'azione corrispondente
        """
        param: str = self.__params__[index]
        for p, a in zip(list_params, list_actions):
            if param in p:
                a()
                return

        print(f'Argomento incorretto nella posizione {index}')
        self.call_help()

    def get_param(self, index: int) -> str:
        """
        ottiene il parametro alla posizione x
        :param index: posizione del parametro
        :return: il parametro
        """
        return self.__params__[index]

    def check(self, param: list | str) -> bool:
        """
        controlla se esiste un parametro o delle sue varianti nel codice
        :param param: parametro/i da controllare
        :return: True se esiste almeno un parametro (e lista) altrimenti se esiste
        """
        if type(param) is str:
            return param in self.__params__
        else:
            for p in param:
                if p in self.__params__:
                    return True
            return False

    def call_help(self) -> None:
        """
        esegue una chiamata all'help e poi esce
        """
        if self.__help_fn__ is not None:
            self.__help_fn__()
            exit(0)

    def get_if(self, index: int, condition: bool, on_false: object=None) -> str | object:
        """
        ritorna un argomento solo se la condizione è vera, se falsa ritorna on_false
        :param index: indice dell'argomento da ritornare
        :param condition: condizione da controllare
        :param on_false: oggetto da ritornare se la condizione corrisponde a False
        :return: self.__params__[index] if condition else on_false
        """
        return self.__params__[index] if condition else on_false

    def __len__(self) -> int:
        """
        override del metodo len, chiamando con il metodo built-in len() restituirà la lunghezza della lista
        :return: lunghezza della lista
        """
        return len(self.__params__)