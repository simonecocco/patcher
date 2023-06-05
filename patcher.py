#!/usr/bin/python3

from os.path import join, exists
from options import configure_argparse
from credits import print_credit
from docker_services import *
from json import loads
from os import getcwd
from log import output, error, warning
from sys import exit

class ActionBuilder:
    actions = ['configure']

    def __init__(self, params):
        self.action = params.remove(0) if params[0] in ActionBuilder.actions else None
        self.files = params

    def __configure_services__(self, verbose=False, dockerv2=False):
        servs = scan_for_services(verbose)
        servs_disk = scan_disk_for_services(verbose)
        register_services(servs, servs_disk, verbose, dockerv2=dockerv2)

    def __load_services__(self, verbose=False):
        output('Caricamento servizi...', verbose)
        json_path = join(getcwd(), 'services.json') if 'patcher' in getcwd() else join(getcwd(), 'patcher.py', 'services.json')
        if not exists(json_path):
            error('Servizi non configurati, configurali con \'python3 patcher.py configure\'')
            exit(1)
        with open(json_path, 'r') as f:
            tmp = '\n'.join(f.readlines())
        servs = loads(tmp)
        servs = [Service(d['disk_path'], d['port'], d['name'], d['alias']) for d in servs]
        output(f'Presenti {len(servs)} servizi', verbose)
        return servs

    def __split_params_to_services__(self, servs, param, strict=False):
        def compare(servs, name):
            serv_name = name.split('=')[0] if '=' in name else name
            mini_serv_name = serv_name.split('/')[0]
            serv_name = serv_name.lower()
            for i, serv in enumerate(servs):
                if serv_name.startswith(serv.disk_path.lower()):
                    return i
                # previene l'identificazione errata tramite file
                if serv.name.lower() in mini_serv_name or serv.alias.lower() in mini_serv_name:
                    return i

            return None

        d = [(serv, []) for serv in servs]
        for cmd in param:
            index = compare(servs, cmd)
            if index is None:
                warning(f'Il comando {cmd} non fa riferimento ad alcun servizio conosciuto')
                if strict:
                    exit(1)
                else:
                    continue
            d[index][1].append(cmd)
        return d


    def run(self, verbose=False, dockerv2=False, strict=False, all_yes=False, no_bkp=False, no_docker=False, hard_build=False):
        if self.action is None:
            servs = self.__load_services__(verbose=verbose)
            d = self.__split_params_to_services__(servs, self.files, strict)
            d = list(filter(lambda e: len(e[1]) > 0, d))
            for t in d:
                t[0].apply_patch(t[1], all_yes=all_yes, no_bkp=no_bkp, no_docker=no_docker, hard_build=hard_build, verbose=verbose, strict=strict)
        elif self.action == ActionBuilder.actions[0]:
            self.__configure_services__(verbose, dockerv2)

if __name__ == '__main__':
    opt = configure_argparse().parse_args()

    if not opt.quiet:
        print_credit()

    action = ActionBuilder(opt.params)
    action.run(verbose=opt.verbose, dockerv2=opt.docker2, strict=opt.strict, all_yes=opt.yes, no_bkp=opt.no_bkp, no_docker=opt.no_docker, hard_build=opt.hard_build)
