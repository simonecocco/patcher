from os.path import join, exists
from adpatcher.options import configure_argparse
from adpatcher.credits import print_credit
from adpatcher.docker_services import *
from adpatcher.utils import call_process
from json import loads
from os import getcwd, geteuid
from adpatcher.utils.stdout_utils import output, error, warning
from sys import exit

class ActionBuilder:
    actions = {
        # Configura i vari servizi
        'configure': lambda self, verbose, dockerv2,: self.__configure_services__(verbose, dockerv2),
        # Fornisce una panoramica dei servizi
        'sysadmin': lambda self, verbose, dockerv2: self.__show_sysadmin_panel__(verbose, dockerv2) # forse da rendere di default se è stato già configurato
    }

    # Costruttore della classe
    def __init__(self, params):
        # Controlla se il primo parametro è un'azione e lo memorizza
        self.action = params.pop(0) if params[0] in ActionBuilder.actions.keys() else None
        # Il resto sono file da modificare
        self.files = params

    # Configura i servizi
    def __configure_services__(self, verbose=False, dockerv2=False):
        output('Configurazione servizi...', verbose)
        servs = scan_for_services(verbose)
        servs_disk = scan_disk_for_services(verbose)
        register_services(servs, servs_disk, verbose, dockerv2=dockerv2)

    def __show_sysadmin_panel__(self, verbose=False, dockerv2=False):
        output('Loading sysadmin panel...', verbose)
        servs = self.__load_services__(True)
        container_status, _ = call_process('docker', ['ps', '-a', '--format', 'table {{.Names}}\t{{.Status}}']) # controlla per exit o dead
        container_resources, _ = call_process('docker', ['stats', '--no-stream', '--format', 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}'])
        # implementa la visualizzazione dei log per ogni servizio. nei log cerchi la parola chiave che indica un errore
        # da là fai comparire il fatto che sia presente

    def __load_services__(self, verbose=False):
        output('Caricamento servizi...', verbose)
        json_path = join(getcwd(), 'services.json') if 'patcher' == getcwd()[-len('patcher'):] else join(getcwd(), 'patcher', 'services.json')
        if not exists(json_path):
            error('Servizi non configurati, configurali con \'sudo patcher configure\'')
            exit(1)
        with open(json_path, 'r') as f:
            tmp = '\n'.join(f.readlines())
        servs = loads(tmp)
        servs = [Service(d['disk_path'], d['port'], d['name'], d['alias'], id=['id'], verbose=verbose) for d in servs]
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
        else:
            # Esegue l'azione specificata
            ActionBuilder.actions[self.action](self, verbose, dockerv2)
