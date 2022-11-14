from json import dumps, loads
import os
from utils import is_valid_file, call_process
import log
from sys import exit
import re
import makefile

class Service:
    def __init__(self, directory: str, name: str, in_port: str, out_port: str, alias: str = '') -> None:
        self.path: str = directory
        self.name: str = name
        self.alias: str = name if alias == '' or alias is None else alias
        self.port: tuple[int, int] = (int(in_port), int(out_port))

    def service_copy() -> int: #ritorna la versione
        pass

    def restore_bkp(target_version: int, skip_files: list[str], interactive: bool = True) -> None:
        pass

    #TODO

JSON_FILE_NAME: str = 'services.json'

def __restorefromjson__(path: str) -> list[Service]:
    tmp: str
    with open(path, 'r') as f:
        tmp = f.read()
        f.close()
    services_list: list[Service]
    return [Service(**service) for service in loads(tmp)]

def __getpossibleservices__(path: str) -> list[str]:
    content: list[str] = os.listdir(path if len(path) > 0 else '.')
    content = map(lambda x: os.path.join(path, x), content)
    res: list[str] = filter(lambda x: os.path.isdir(x) and os.path.exists(os.path.join(x, 'docker-compose.yml')), content)
    return res

def __getfromdocker__(path: str) -> list[Service]:
    def get_ports(ports: str) -> list[str]:
        ports = ports.split('/')[0]
        ports = ports.split(':')[1]
        return ports.split('->')

    out, err = call_process('docker', ['ps', '--format', 'table ID:{{.ID}},NAME:{{.Image}},STATUS:{{.Status}},PORTS:{{.Ports}}'])
    if len(err) > 0:
        log.error('Per configurare i processi è automaticamente è necessario essere utente root.')
        exit(1)
    out = out.split('\n')[1:]
    regex: str = '^ID:([A-Fa-f0-9]{1,}),NAME:([\S]{1,}),STATUS:([\w\d()\s]{1,}),PORTS:([\d\.]{7}:\d{1,}->\d{1,}\/\w{1,})'
    services_list: list[Service] = []
    for serv_detail in out:
        detail = re.findall(regex, serv_detail)
        if len(detail) == 0:
            continue
        detail = detail[0]
        services_list.append(Service(None, detail[1], *get_ports(detail[3])))
    direct: list[str] = __getpossibleservices__(path)
    for i, serv in enumerate(services_list):
        
    return services_list


def __saveservices__(path: str, services: list[Service]) -> None:
    tmp: list[dict] = [{'directory':s.path, 'name':s.name, 'in_port':str(s.port[0]), 'out_port':str(s.port[1]), 'alias':s.alias} for s in services]
    with open(path, 'w') as config:
        config.write(dumps(tmp))
        config.close()

def get_services(path: str) -> list[Service]:
    script_path: str = os.path.join(path, JSON_FILE_NAME)
    tmp: list[Service] = __restorefromjson__(script_path) if is_valid_file(script_path) else __getfromdocker__(path)
    __saveservices__(script_path, tmp)
    return tmp
