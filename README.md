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

### Alias dei servizi
Patcher è un software che si occupa in autonomia di prendere e associare i vari servizi presenti nel disco. Per questo motivo è possibile associare un alias al servizio per poterlo richiamare in maniera più veloce. Guarda la sezione **service** per più informazioni.

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

In caso di differenti file da modificare in un unico colpo sarà sufficiente specificare più file, con i loro relativi servizi:
```bash
patcher edit MySuperService/src/app.py app_fixed.py MySuperService/src/Dockerfile ../new_dockerfile AnotherSuperService/README.md modified_readme.md
```

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

E' possibile applicare la modalità sos infinite volte.

## Comando reconfigure
Con il comando reconfigure è possibile reinizializzare i servizi aggiungendoli manualmente:
```bash
patcher reconfigure /my_path/AnotherService/ /my_path/AnotherService2
```
Questo ricercherà tutte le directory dei servizi includendo pure le due specificate

## Comando fix
Il comando fix ha la possibilità di gestire le modifiche del servizio in maniera rapida.

In particolare:
* consente di suggerire una correzione automatica per una riga dove è presente il bug
```bash
patcher fix MySuperService/file 43-53
```
> Suggerisci un fix dalla linea 43 alla 53 del file `MySuperService/file`

* Consente di segnare come fixato il servizio:
```bash
patcher fix MySuperService
```

## Comando sysadmin
Il comando sysadmin mostra alcune statistiche sul servzio:
```bash
patcher sysadmin [INFO] <service name/alias/path>
```

Dove `INFO` può essere:
* spazio sul disco - `disk`
* utilizzo ram - `ram`
* cpu utilizata - `cpu`