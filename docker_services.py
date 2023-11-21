from json import dumps
from utils import call_process
from sys import exit
from log import error, output, warning, diff_output
from os import listdir, getcwd, chdir
from os.path import join, isdir, exists, abspath, dirname, basename
from makefile import Makefile
from time import sleep

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

    def __update_file__(self, original, new, no_bkp=False, all_yes=False, verbose=False):
        if not exists(original) or not exists(new):
            return False
        if not all_yes:
            """La riga ha un bug: non mostra realmente le differenze
            with open(original, 'r') as f:
                orig = f.read()
            with open(new, 'r') as f:
                new_content = f.read()

            diff_output('FILE ORIGINALE', orig, 'FILE NUOVO', new_content)
            """
            orig_file_content, _ = call_process('xxd', [original])
            with open('/tmp/diff_file1.txt', 'w') as f:
                f.write(orig_file_content)
            new_file_content, _ = call_process('xxd', [new])
            with open('/tmp/diff_file2.txt', 'w') as f:
                f.write(new_file_content)
            diff_out, _ = call_process('diff', ['/tmp/diff_file1.txt', '/tmp/diff_file2.txt'])
            diff_out = [line.strip() for line in diff_out.split('\n')]
            orig_diff = '\n'.join([line[2:] for line in diff_out if line.startswith('<')])
            new_diff = '\n'.join([line[2:] for line in diff_out if line.startswith('>')])
            diff_output('FILE ORIGINALE', orig_diff, 'FILE NUOVO', new_diff)
            warning('Applico le modifiche? [y/n] ')
            risposta = input()
            if risposta.lower() != 'y':
                return False

        if not no_bkp:
            dir, fn = dirname(original), basename(original)
            count = 0
            while exists(join(dir, f'.{fn}.bkp{count}')):
                count += 1
            output(f"Eseguo backup in {join(dir, f'.{fn}.bkp{count}')}", verbose)
            call_process('mv', [original, join(dir, f'.{fn}.bkp{count}')])
        out, err = call_process('cp', [new, original])
        if len(err) > 0:
            error('Errore, ri applico il precedente file')
            call_process('mv', [join(dir, f'.{fn}.bkp{count}'), original])
            return False
        else:
            output('Completato', verbose)
            return True

    def __restore_file__(self, file_path, version, no_bkp=False, all_yes=False, verbose=False):
        original = file_path
        dir, fn = dirname(original), basename(original)
        if version < 0:
            count = -1
            while True:
                if exists(join(dir, f'.{fn}.bkp{count+1}')):
                    count += 1
                else:
                    break
            if count < 0:
                warning('Non esiste una versione base')
                return False
            new = join(dir, f'.{fn}.bkp{count}')
        else:
            new = join(dir, f'.{fn}.bkp{version}')
        return self.__update_file__(original, new, no_bkp=no_bkp, all_yes=all_yes, verbose=verbose)

    def __checkpoint__(self): #todo
        raise NotImplementedError('Modalità checkpoint non ancora implementata')

    def __str__(self):
        return self.disk_path

    def __repr__(self):
        return str(self)

    def apply_patch(self, file_list, all_yes=False, no_bkp=False, no_docker=False, hard_build=False, verbose=False, strict=False):
        def get_real_path(file_path):
            if exists(file_path):
                return file_path
            else:
                ffp = file_path.lower()
                if self.alias.lower() in ffp and (index := ffp.find(self.alias.lower())) != -1:
                    index += len(self.alias)
                    return join('/', *self.disk_path.split('/'), *file_path[index:].split('/'))
                elif self.name.lower() in ffp and (index := ffp.find(self.name.lower())) != -1:
                    index += len(self.alias)
                    return join('/', *self.disk_path.split('/'), *file_path[index:].split('/'))
                
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
            result = False
            if cmd[1] is None:
                result = self.__checkpoint__()
                break
            elif type(cmd[1]) is int:
                result = self.__restore_file__(cmd[0], cmd[1], no_bkp, all_yes, verbose)
            elif type(cmd[1]) is str:
                result = self.__update_file__(cmd[0], cmd[1], no_bkp, all_yes, verbose)
            if not result:
                error(f'Problema con {cmd[0]}')
                if strict:
                    exit(1)

        output('Applicazione completa', verbose)
        if not no_docker:
            if hard_build:
                output('Eseguo riavvio completo del servizio', verbose)
                self.mk.docker_hardreboot()
            else:
                output('Eseguo soft reboot del servizio', verbose)
                self.mk.docker_softreboot()
            #release = False
            #while not release:
            #    ser = scan_for_services(v=False, select=self.name)[0]
            #    print(f'Status servizio: {ser["status"]}')
            #    if 'up' in ser['status'].lower():
            #        release = True
            output('Completato', verbose)


def scan_for_services(v=False, select=None):
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
    return [get_information(row) for row in out if select is None or select in row]

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
