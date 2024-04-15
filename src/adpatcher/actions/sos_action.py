from adpatcher.services import Service

def SOS(target_service: Service) -> None:
    target_service.sos()