from adpatcher.services import Service

for target_service_alias in args.params[1:]:
            current_selected_service: Service = select_service_based_on_alias(services, target_service_alias)
            if current_selected_service is None:
                error(f'Servizio non trovato: {target_service_alias}')
                continue
            warning(f'Servizio {current_selected_service.alias} in modalità sos')
            current_selected_service.sos()
            output(f'Servizio {current_selected_service.alias} in modalità sos completato', verbose=args.verbose)

def select_service_by_alias(services_list: list, alias: str) -> Service:
