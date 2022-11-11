# patcher
> Gestione delle patch per Attacco/Difesa

# A cosa serve?
Questo file semplifica la gestione delle patch dei servizi. Esso permette di patchare uno o più file per poi ritornare indietro con le versioni.

# Come si usa?
Il file deve essere posizonato nella directory home dove son presenti i servizi delle AD

Per invocarlo si usa `./patcher.py` o `python3 patcher.py`.
```Shell
python3 patcher.py AZIONI argomento1 argomento2 OPZIONI
```

# Azioni disponibili
## Patch di un file (`apply` o `a`)
```Shell
python3 patcher.py a /percorso/per/il/file nuovo_file
```

> esempio: `python3 patcher.py a CyberUni/examnotes/Dockerfile new_dockerfile`
>
> Questo esempio prende `new_dockerfile` e lo piazza dentro `CyberUni/examnotes` facendo il backup del precedente Dockerfile.

## Versione precedente di un file (`back` o `b`)
```Shell
python3 patcher.py b percorso/per/il/file versione
```

> esempio: `python3 patcher.py b CyberUni/examnotes/Dockerfile -1`
>
> Questo esempio sostituisce `CyberUni/examnotes/Dockerfile` con la sua versione precedente.

> esempio 2: `python3 patcher.py b CyberUni/examnotes/Dockerfile 0`
>
> Questo esempio sostituisce `CyberUni/examnotes/Dockerfile` con la sua versione 0.

## Patch multiple (`file` o `f`)
Considerando un semplice file .txt
```Plaintext
/percorso/per/file1 file1_patch
/percorso/per/file2 file2_patch

/percorso2/file1 altro_file_patch
```

Il file di esempio qua sopra contiene varie istruzioni di patch (percorso file originale e percorso nuovo file).

Quando vengono patchati più servizi è necessario dividerli con una newline vuota in modo che il programma riconosca quando due servizi diversi vengono modificati.

Dopo creato il semplice file è possibile applicarlo con

```Shell
python3 patcher.py f file.txt
```

# Opzioni disponibili
* `-q`: non mostra i crediti e la versione
* `--no-bkp`: serve a non far fare il backup della patch corrente in caso di ripristino
* `--no-docker`: una volta finita l'operazione con i file non eseguirà la compilazione con docker
* `--hard-build`: distrugge il container e lo riporta su (da utilizzare solo in caso di necessità). Per utilizzarla è necessario non sia presente `--no-docker`
* `--back` o `-b`: usabile solo con file, serve per annullare un gruppo di patch (uguale a b \[files\] -1)
