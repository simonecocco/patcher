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

### Applicazione di una patch ad un file
> La sintassi per l'applicazione della patch è `old_file=new_file`. old_file deve essere necessariamente un file esistente all'interno del servizio, non è possibile operare al di fuori.
>
> Allo stesso modo old_file può essere composto in diversi modi: `absolute_path_to_file` o `<service_alias>/relative_path_to_file` o `relative_path_to_file`.
> 
> Il new_file invece sarà un percorso relativo o assoluto del file contenente la patch.

#TODO

# Opzioni disponibili
* `-q`: non mostra i crediti e la versione
* `--no-bkp`: serve a non far fare il backup della patch corrente in caso di ripristino
* `--no-docker`: una volta finita l'operazione con i file non eseguirà la compilazione con docker
* `--hard-build`: distrugge il container e lo riporta su (da utilizzare solo in caso di necessità). Per utilizzarla è necessario non sia presente `--no-docker`
* `-v` o `--verbose`: mostra un output dettagliato
* `-y`: non chiede l'autorizzazione all'utente

# Opzioni makefile
