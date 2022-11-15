from json import dumps, loads
import os
from utils import is_valid_file, call_process
import log
from sys import exit
import re
from makefile import Makefile
import utils
import secrets

class Service:
    def __init__(self, directory: str, name: str, in_port: str, out_port: str, alias: str = '') -> None:
        self.path: str = directory
        self.name: str = name
        self.alias: str = name if alias == '' or alias is None else alias
        self.port: tuple[int, int] = (int(in_port), int(out_port))
        self.instr: list[str] = []

    def service_copy(self, do_not_overwrite: bool = True) -> None:
        # todo da aggiornare con le versioni dei checkpoint
        utils.do_checkpoint_backup(self.path, do_not_overwrite)

    def restore_bkp(self, target_version: int, skip_files: list[str], interactive: bool = True, strict: bool = True) -> None:
        if interactive:
            if 'y' != input(f'Vuoi ripristinare {self.alias} alla versione {target_version}? '):
                if strict:
                    log.error('Annullato')
                    exit(1)
                else:
                    log.warning('Annullato')
                    return

        # salvo i file da tenere
        dirname: str = f'/tmp/{secrets.token_hex(8)}'
        call_process('mkdir', ['-p', dirname])
        log.output(f'Uso {dirname}')
        for sf in skip_files:
            relative_path: str = sf.removeprefix(self.path).removeprefix('/')
            absolute_backup_path: str = os.path.join(dirname, '/'.join(relative_path.split('/')[:-1]))
            call_process('mkdir', ['-p', absolute_backup_path])
            call_process('cp', [sf, tmp:=os.path.join(dirname, relative_path), '--preserve=mode,ownership,timestamps'])
            print(f'Salvo {tmp}')
        


    def execute_instruction(self, interactive: bool = True, backup: bool = True, docker_update: bool = True, docker_hard_reboot: bool = False, strict: bool = False) -> None:
        file_to_restore: list = [] #tuple
        file_to_keep: list = [] #solo stringhe
        file_to_patch: list = [] #tuple
        log.output('Applico la patch')
        for instr in self.instr:
            param2_type = type(instr[1])
            if param2_type is str:
                file_to_patch.append(instr)
            elif param2_type is int:
                file_to_restore.append(instr)
            elif instr[1] is None:
                file_to_keep.append(instr[0])
            else:
                log.error(f'wtf bro {instr[1]}')
                exit(1)
        
        tmp = list(filter(lambda t: t[0] == self.path or t[0][:-1] == self.path, file_to_restore))
        if len(tmp) > 0: # ripristino dal checkpoint del servizio
            self.restore_bkp(tmp[0][1], file_to_keep, interactive, strict)
            file_to_restore.remove(tmp)
        #TODO

    def __str__(self) -> str:
        return f'{self.name} ({self.alias}) located at: {self.path}, listen in: {self.port}'

    def __repr___(self) -> str:
        return self.__str__() 

    def get_makefile(self) -> Makefile:
        return Makefile(os.path.join(self.path, 'makefile'))

    def __hash__(self) -> str:
        return self.name

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
    content = list(map(lambda x: os.path.join(path, x), content))
    res: list[str] = list(filter(lambda x: os.path.isdir(x) and os.path.exists(os.path.join(x, 'docker-compose.yml')), content))
    return res

def __getfromdocker__(path: str) -> list[Service]:
    print(path)
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
    direct: list[str] = __getpossibleservices__('/'.join(path.split('/')[:-1]) if path.endswith('patcher') else path)
    print('Services:')
    for i, serv in enumerate(services_list):
        service_name: str = serv.name.lower()
        for d in direct:
            actual_name: str = d.split('/')[-1].lower()
            if actual_name in service_name:
                services_list[i].path = d
                services_list[i].alias = actual_name
                break
        else:
            continue
        print(serv)
    return list(filter(lambda ser: ser.path is not None, services_list))


def __saveservices__(path: str, services: list[Service]) -> None:
    tmp: list[dict] = [{'directory':s.path, 'name':s.name, 'in_port':str(s.port[0]), 'out_port':str(s.port[1]), 'alias':s.alias} for s in services]
    with open(path, 'w') as config:
        config.write(dumps(tmp))
        config.close()

def get_services(current_dir: str, script_path: str, update: bool = False) -> list[Service]:
    script_path: str = os.path.join(script_path, JSON_FILE_NAME)
    tmp: list[Service] = __restorefromjson__(script_path) if is_valid_file(script_path) and not update else __getfromdocker__(current_dir)
    __saveservices__(script_path, tmp)
    return tmp

def search_for_service(target: str, services: list[Service]) -> list[Service, str]:
    if '/' in services and os.path.exists(target): #è un percorso relativo o assoluto
        if os.path.isdir(target):
            log.error(f'Directory non consentite ({target})')
            exit(1)
        absolute: str = os.path.abspath(target)
        for s in services:
            common_path: str = os.path.commonprefix([absolute, s.path])
            if common_path == s.path:
                return s, absolute
    elif '/' in services and not os.path.exists(target): #è un percorso che contiene alias
        prefix: str = target.split('/')[0]
        for s in services:
            if prefix.lower() in s.name.lower() or prefix.lower() == s.alias.lower():
                return s, os.path.join(s.path, '/'.join(target.split('/')[1:]))
    elif '/' not in services and os.path.exists(target): #è un file relativo o una directory relativa
        absolute: str = os.path.abspath(target)
        if os.path.isdir(absolute):
            for s in services:
                if absolute == s.path:
                    return s, absolute
        else:
            for s in services:
                common_path: str = os.path.commonprefix([absolute, s.path])
                if common_path == s.path:
                    return s, absolute
    else: #se non esiste nè è un percorso -> probabili un nome servizio o un file inesistente
        prefix: str = target.split('/')[0]
        for s in services:
            if prefix.lower() in s.name.lower() or prefix.lower() == s.alias.lower():
                return s, os.path.join(s.path, '/'.join(target.split('/')[1:]))

    return None
