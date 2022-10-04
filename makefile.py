import os
import utils

makefile_content: str = '''
all: build up
build:
    sudo docker-compose build
up:
    sudo docker-compose up --build -d
down:
    sudo docker-compose down
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
        self.service_mf_path: str = os.path.join(service_path, 'makefile')
        if not utils.is_valid_file(self.service_mf_path):
            mkfile_tmp = open(self.service_mf_path, 'w')
            mkfile_tmp.write(makefile_content)
            mkfile_tmp.close()

    def 



