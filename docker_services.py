from json import dumps
from utils import call_process
from sys import exit
from log import error, output, warning
from os import listdir, getcwd, chdir
from os.path import join, isdir, exists, abspath
from makefile import Makefile

class Service:
    def __init__(self, disk_path, port, name, alias, dockerv2=False, verbose=False):
        self.disk_path = abspath(disk_path)
        self.port = port
        self.name = name
        self.alias = alias
        self.mk = Makefile(self.disk_path, docker_v2=dockerv2, verbose=verbose)

    def to_dict(self):
        return {
            'disk_path':self.disk_path,
            'port':self.port,
            'name':self.name,
            'alias':self.alias
        }

    def __update_file__(self, original, new): #todo
        pass

    def __restore_file__(self, file_path, version): #todo
        pass

    def __checkpoint__(self): #todo
        pass

    def __str__(self):
        return self.disk_path

    def __repr__(self):
        return str(self)

    def apply_patch(self, file_list, all_yes=False, no_bkp=False, no_docker=False, hard_build=False, verbose=False, strict=False):
        def get_real_path(file_path):
            if exists(file_path):
                return file_path
            else:
                print(self.disk_path, file_path)
                ffp = file_path.lower()
                if self.alias.lower() in ffp and (index := ffp.find(self.alias.lower())) != -1:
                    index += len(self.alias)
                    return join(*self.disk_path.split('/'), *file_path[index:].split('/'))
                elif self.name.lower() in ffp and (index := ffp.find(self.name.lower())) != -1:
                    index += len(self.alias)
                    return join(*self.disk_path.split('/'), *file_path[index:].split('/'))
                
                error(f'Il file {file_path} non esiste')
                exit(1)

        def get_file_path(cmd):
            if '=' in cmd:
                origin, new = cmd.split('=')
                origin = get_real_path(origin)
                try:
                    new = int(new)
                except:
                    new = get_real_path(new)

                return [origin, new]
            else:
                return [get_real_path(cmd), None]
        
        output(f'Applicazione patch per {self.alias}', verbose)
        for istr in file_list:
            cmd = get_file_path(istr)
            if cmd[1] is None:
                self.__checkpoint__()
            elif type(cmd[1]) is int:
                self.__restore_file__(*cmd)
            elif type(cmd[1]) is str:
                self.__update_file__(*cmd)

def scan_for_services(v=False):
    def get_information(row):
        s = row.split(',')
        return {
            'id':s[0].split(':')[1],
            'name':s[1].split(':')[1],
            'status':s[2].split(':')[1],
            'ports':s[3].split('PORTS:')[1]
        }

    output('Caricamento servizi', verbose=v)
    out, err = call_process('docker',
        ['ps',
        '--format',
        'table ID:{{.ID}},NAME:{{.Image}},STATUS:{{.Status}},PORTS:{{.Ports}}'
        ])
    if len(err) > 0:
        error(f'Errore durante la chiamata a docker.\nTraceback\n{err}')
        exit(1)

    output('Fatto', v)

    out = out.split('\n')[1:-1]
    return [get_information(row) for row in out]

def scan_disk_for_services(v=False):
    output('Localizzazione servizi su disco', v)
    prefix = '.'
    if 'patcher' in getcwd():
        prefix = '..'
    dirs = listdir(prefix)
    dirs = list(filter(lambda d: 'patcher' not in d and isdir(d:=join(prefix, d)) and exists(d), dirs))
    return dirs

def register_services(docker_info, disk_info, v=False, dockerv2=False):
    current_wd = getcwd()
    if 'patcher' in current_wd:
        chdir('..')
    servs = []
    for info in disk_info:
        l = info.lower()
        for s in docker_info:
            if l in s['name']:
                servs.append(Service(info, s['ports'], s['name'], info.lower(), dockerv2=dockerv2, verbose=v))
                break
        else:
            warning(f'Nessun servizio compatibile con {info} trovato')

    if 'patcher' not in current_wd:
        current_wd = join(current_wd, 'patcher')
    with open(join(current_wd, 'services.json'), 'w') as f:
        f.write(dumps([service.to_dict() for service in servs]))
        f.close()
    output(f'Servizi mappati e salvati in {join(current_wd, "services.json")}', v)
