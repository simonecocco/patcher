import os
import utils

makefile_content: str = '''all: build up
build:
    sudo docker-compose build
up:
    sudo docker-compose up --build -d
down:
    sudo docker-compose down
soft: build up
hard: build down up
log:
    sudo docker-compose logs

'''


class Makefile:
    def __init__(self, service_path: str, create_if_not_exist: bool=True) -> None:
        """
        Crea un file makefile nel caso non ci sia
        :param service_path path del servizio
        :param create_if_not_exist 
        """
        self.service_mf_path: str = service_path if service_path.endswith('makefile') else os.path.join(service_path, 'makefile')
        print(f'Using {self.service_mf_path} as makefile')
        if not utils.is_valid_file(self.service_mf_path):
            mkfile_tmp = open(self.service_mf_path, 'w')
            mkfile_tmp.write(makefile_content)
            mkfile_tmp.close()

    def __callmake__(self, target) -> None:
        utils.call_process('make', ['-C', self.service_mf_path, target])

    def __docker_up__(self) -> None:
        self.__callmake__('up')

    def __docker_down__(self) -> None:
        self.__callmake__('down')

    def docker_hardreboot(self) -> None:
        self.__callmake__('hard')

    def docker_softreboot(self) -> None:
        self.__callmake__('soft')
