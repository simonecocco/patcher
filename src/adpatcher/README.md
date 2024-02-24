# patcher
> Gestione delle patch per Attacco/Difesa

# A cosa serve?
Questo file semplifica la gestione delle patch dei servizi. Esso permette di patchare uno o più file per poi ritornare indietro con le versioni.

# Come si usa?
Il file deve essere posizonato nella directory home dove son presenti i servizi delle AD

Per invocarlo: `python3 patcher.py`.
```Shell
python3 patcher.py args
```

# Azioni disponibili
## Configurazione dei servizi

Quando viene avviato senza argomenti, _patcher_ trova automaticamente e mappa i servizi (porte, nome e percorso) su un file json che utilizzerà ogni volta patcher sarà richiesto.

Per essere considerato servizio, deve riuscire a localizzarlo nel disco e a mapparlo nei servizi attivi di docker.

Quando il servizio è mappato correttamente viene inserito un makefile che consente di gestire il docker in maniera rapida (vedi sezione **makefile**).
```shell
python3 patcher.py
```

Struttura del file json generato
```javascript
[
    {
        'directory':s.path, //Percorso dove si trovano i sorgenti del servizio
        'name':s.name, //Nome del servizio
        'in_port':str(s.port[0]), //Porta interna
        'out_port':str(s.port[1]), //Porta esterna
        'alias':s.alias //Nome del servizio (mnemonico)
    },
    ...
]
```
> Il file json viene generato in `patcher/services.json`

## Edit dei servizi
I servizi possono essere editati:
* manualmente nel file services.json
* automaticamente usando `python3 patcher.py configure`

### Configure
Usando configure viene usato un for-loop per iterare fra i servizi e modificare gli alias assegnati. Per terminare l'assegnazione è sufficiente usare CTRL+C.

## Checkpoint
Una volta che il servizio funziona correttamente, si può salvare il sorgente del servizio usando il comando `checkpoint`.

Questo comando consente di fare un backup del sorgente da cui recuperare i file nel caso di eventuale eliminazione o rottura del servizio.

### Uso
```python
python3 patcher.py alias_servizio
# oppure
python3 patcher.py nome_servizio
# oppure
python3 patcher.py path_del_servizio
```

## Applicazioni di patch e gestione delle versioni
Ogni file può essere modificato in avanti (applicando una patch) o all'indietro (ripristinando una versione).

Prendiamo per esempio un'albero di file di alcuni servizi d'esempio:

Serv1/
-> main.py
-> img/
--> loader.py

Serv2/
-> wifi_loader
-> README.md

### Applicazione di una patch ad un file
> La sintassi per l'applicazione della patch è `old_file=new_file`. old_file deve essere necessariamente un file esistente all'interno del servizio, non è possibile operare al di fuori.
>
> Allo stesso modo old_file può essere composto in diversi modi: `absolute_path_to_file` o `<service_alias>/relative_path_to_file` o `relative_path_to_file`.
> 
> Il new_file invece sarà un percorso relativo o assoluto del file contenente la patch.

> _Esempio: ho sistemato il file loader.py creando un nuovo file_ `patch_loader.py` _e lo voglio applicare_

```shell
python3 patcher.py alias_serv1/img/loader.py=../patch_loader.py
```
Oppure
```shell
python3 patcher.py Serv1/img/loader.py=../patch_loader.py
```

> Più file possono essere patchati contemporaneamente, aggiungendo dei file

```shell
python3 patcher.py old_file1=new_file1 old_file2=new_file2 ...
```

### Ripristino di una versione precedente
> Le regole di scrittura di old_file sono uguali alla sezione di patch.

Per il ripristino di un file, è necessario specificare il file richiesto per poi determinarne la versione.

> _Esempio: vogliamo che loader.py torni alla versione pre patch_
```shell
python3 patcher.py Serv1/img/loader.py=-1
```

> _Esempio2: vogliamo che un file torni alla sua versione n.3_
```shell
python3 patcher.py file=2
```

Anche qua è possibile ripristinare più file:
```shell
python3 patcher.py file1=target_version1 file2=target_version2 ...
```

### Opzione speciale: ripristino di un servizio da un checkpoint
Questa è un'opzione speciale che è presente nella parte di ripristino.

Infatti se si specifica il nome del servizio e la versione (`Serv1=versione`) è possibile ripristinare l'intero servizio a quella versione.

Se però è stata applicata una patch e si vuole preservare il file patchato è possibile escludere quel file (o più file) dal ripristino.

```shell
python3 patcher.py Serv1=-1 file1_to_preserve file2_to_preserve
```

In aggiunta a questo, dopo il ripristino possono anche essere eseguite delle patch!!

```shell
python3 patcher.py Serv1=-1 file1_to_preserve file_to_patch=path_to_patch
```

# Opzioni disponibili
* `-q`: si avvia in modo silenzioso, non mostra crediti e versione
* `--no-bkp`: non esegue il backup del file prima di sostituirlo con la versione di patch
* `--no-docker`: una volta finita l'operazione con i file non eseguirà la compilazione con docker
* `--hard-build`: porta giù il container e lo riporta su (comporta l'eliminazione dei dati non salvati). Per utilizzarla è necessario non sia presente `--no-docker`
* `-v` o `--verbose`: stampa diversi output
* `-y`: non chiede conferma all'utente su una determinata operazione ma la esegue automaticamente
* `--strict`: 

# Opzioni makefile
> Il makefile viene creato all'interno di ogni servizio automaticamente.

## Softreboot del servizio
Il makefile contiene una scorciatoia per eseguire il soft reboot del servizio.

```shell
make soft
```
> Il comando di prima equivale a `sudo docker-compose build && sudo docker-compose up --build -d`

## Hardreboot del servizio
> Attenzione, l'hard reboot cancella tutti i dati non salvati in volumi.

```shell
make hard
```

> Il comando di prima equivale a `sudo docker-compose build && sudo docker-compose down && sudo docker-compose up --build -d`
