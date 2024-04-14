# patcher
> Il migliore amico dei SysAdmin durante le gare di Attacco/Difesa.

## Installazione
### PyPI
Patcher può essere installato direttamente da PyPI tramite pip:
```bash
pip3 install adpatcher
```

### Installazione dal sorgente
Oppure può essere scaricato e buildato manualmente:
```bash
git clone https://github.com/simonecocco/patcher.git
cd patcher
pip3 install .
```

## Utilizzo
Patcher è uno strumento da riga di comando che possiede molteplici funzioni, tra cui:
* gestione delle patch per i servizi di attacco/difesa
* fornisce una panoramica al sysadmin dello stato dei servizi
* semplifica le chiamate a Docker
> guarda la roadmap per sapere quali sono i prossimi passi.

### Patching di un file
Per eseguire la patch di un file all'interno di un servizio è sufficiente specificare il `nome del servizio`, il `file originale da sostituire` e `il nuovo file`.
Qui un esempio:
Supponiamo un servizio così strutturato:
```plaintext
MySuperService/
    src/
        Dockerfile
        app.py
    docker-compose.yml
    README.md
```
e supponiamo di avere scoperto una vulnerabilità dentro `MySuperService/src/app.py`.

Una volta copiato il file in questione e corretta la vulnerabilità la si vuole applicare per testare il servizio. Sarà sufficiente:
```bash
patcher edit MySuperService/src/app.py ./app-fixed.py
```
patcher si occuperà di sostituire il file e riavviare il container in autonomia.

### Rimozione di una patch per un file
Assumendo di avere lo stesso servizio di prima, il sysadmin nota che la patch causa problemi, perciò vuole tornare indietro alla precedente.

Per fare ciò si specifica di quante versioni del servizio tornare indietro:
```bash
patcher edit MySuperService -1
```

Da qua verrà riportato indietro il servizio alla versione precedente e di conseguenza riavviato

## Modalità SOS
In caso di problemi gravi, il sysadmin può decidere di riportare il servizio alla versione originale. Per fare ciò, il comando `sos` esegue una catena di azioni volte a ripristinare lo stato del servizio:
Dopo runnato
```bash
patcher sos MySuperService
```
1. tutte le modifiche in corso vengono salvate
2. vengono ripristinati i file originali
3. il container viene riavviato
4. le modifiche vengono reinserite per continuare la modifica

## Comando reconfigure
Con il comando reconfigure è possibile reinizializzare i servizi aggiungendoli manualmente:
```bash
patcher reconfigure /my_path/AnotherService/ /my_path/AnotherService2
```
Questo ricercherà tutte le directory dei servizi includendo pure le due 