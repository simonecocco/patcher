import json

CONFIG_FILE_NAME: str = 'config.json'

def create(services: dict) -> None:
    with open(CONFIG_FILE_NAME, 'w') as json_config:
        json_config.write(json.dumps(services))

def read() -> dict:
    try:
        res: dict
        with open(CONFIG_FILE_NAME, 'r') as json_config:
            res = json.loads(json_config.read())
            json_config.close()
        return res
    except:
        return None
