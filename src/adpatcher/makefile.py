import os
from os.path import exists
import adpatcher.utils as utils
from adpatcher.log import output, error, debug, warning
from os.path import dirname

makefile_content: str = '''all: build up

build:
\tsudo docker-compose build

up: build
\tsudo docker-compose up --build -d

down:
\tsudo docker-compose down

soft: build up

hard: build down up

log:
\tsudo docker-compose logs

'''



class Makefile:
	__slots__: list = [
		'verbose',
		'service_mf_path'
	]

	def __init__(self, service_path: str, create_if_not_exist: bool=True, docker_v2=False, verbose=False) -> None:
		"""
		Crea un file makefile nel caso non ci sia
		:param service_path path del servizio
		:param create_if_not_exist 
		"""
		self.verbose: bool = verbose
		self.service_mf_path: str = utils.get_makefile_path_for_service(service_path)
		if not exists(self.service_mf_path):
			with open(self.service_mf_path, 'w') as mkfile_tmp:
				output(f'Creo makefile in {self.service_mf_path} (v2? {docker_v2})', verbose)
				if not docker_v2:
					mkfile_tmp.write(makefile_content)
				else:
					mkfile_tmp.write(makefile_content.replace('docker-compose', 'docker compose'))

	def __callmake__(self, target):
		out, err = utils.call_process('make', ['-C', dirname(self.service_mf_path), target])
		print(out, err)
		if len(out) > 0:
			debug(out, self.verbose)
		if len(err) > 0:
			warning(err)
		return out, err

	def __docker_up__(self):
		out, err = self.__callmake__('up')
		return out, err

	def __docker_down__(self):
		out, err = self.__callmake__('down')
		return out, err

	def docker_hardreboot(self):
		out, err = self.__callmake__('hard')
		return out, err

	def docker_softreboot(self):
		out, err = self.__callmake__('soft')
		return out, err

	def __call__(self, action: str):
		return self.__callmake__(action)