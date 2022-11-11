# patcher
> Gestione delle patch per Attacco/Difesa

# A cosa serve?
Questo file semplifica la gestione delle patch dei servizi. Esso permette di patchare uno o più file per poi ritornare indietro con le versioni.

# Come si usa?
Il file deve essere posizonato nella directory home dove son presenti i servizi delle AD

Per invocarlo si usa `./patcher.py` o `python3 patcher.py`.
```Shell
python3 patcher.py args
```

# Azioni disponibili
## Configurazione di servizi
Per facilitare la scrittura, è possibile scrivere degli alias per ogni servizio.

Per fare ciò si può usare `python3 patcher.py configure` per fare sì che il wizard esegua il tutto automaticamente o passare come parametri gli alias in modo da farlo in modo automatico: `python3 patcher.py configure nome1=percorso_cartella1 nome2=percorso_cartella2 ...`.

## Gestione delle patch (o patch multiple)

Il programma patcher, prende diversi argomenti dove ognuno rappresenta un file da _patchare_.

Esempio: `python3 patcher.py percorso_file1=patch_to_file1 percorso_file2=patch_to_file2 ...`

Al posto dei percorsi assoluti o relativi, è consigliato definire degli alias tramite `patcher.py configure`, in modo da sostituire i percorsi dei file con dei nomi più mnemonici.

Esempio `python3 patcher.py nome1/file1=patch_to_file1 nome2/file2=patch_to_file1 ...`

Quando un file viene modificato è possibile ritornare indietro ad una versione precedente, specificando il numero di versione richiesto, o andando a ritroso con numeri < 0.

Esempio: `python3 patcher.py nome1/file1=-1 nome2/file2=0 ...`
> Imposta il file presente nel percorso `nome1/file1` alla versione precedente alla sua ultima patch, e `nome2/file2` alla sua versione originale

Ogni volta che vengono eseguite delle patch, è possibile portare indietro tutto il servizio ad una specifica versione come con un singolo file `patcher.py nome1=-1 ...` (_il servizio viene portato alla sua versione precedente_)

E' inoltre possibile, tenere una specifica versione di un file o impostare una versione separata di esso.

Esempio: `python3 patcher.py nome1=-1 nome1/file1 nome1/file2=0`
> Tutto il servizio denominato nome1 viene portato ad una sua versione precedente;
>
> il file1 presente nel servizio nome1 viene mantenuto inalterato;
>
> e file2 presente nel servizio nome1 viene portato alla versione 0

## Utilizzo di un file
E' possibile utilizzare un file per passare gli argomenti a patcher.

Il file deve avere una sintassi tipo (i commenti sono espressi con il #):
```
percorso_file=versione
percorso_file=nuovo_file
nome1=versione
...
```

Per passare un file di istruzioni è necessario specificare una delle opzioni `-f` o `--file`.

# Opzioni disponibili
* `-q`: non mostra i crediti e la versione
* `--no-bkp`: serve a non far fare il backup della patch corrente in caso di ripristino
* `--no-docker`: una volta finita l'operazione con i file non eseguirà la compilazione con docker
* `--hard-build`: distrugge il container e lo riporta su (da utilizzare solo in caso di necessità). Per utilizzarla è necessario non sia presente `--no-docker`
* `-v` o `--verbose`: mostra un output dettagliato
* `-y`: non chiede l'autorizzazione all'utente
