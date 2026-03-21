# Progetto AI / Swarm
Progetto di Artificial Intelligence/AI Swarm prodotto dal gruppo Antonio Rosano, Angelo Spadola, Marco Spampinato per l'anno accademico 2025/2026

## Get started!
Per iniziare, inizializziamo un ambiente locale Python:
```sh
python -m venv .venv
```
Per attivare l'ambiente, eseguiamo il comando:
```sh
# Su Linux/Mac OS
source .venv/bin/activate

# Su Windows, usando PowerShell
.venv\Scripts\Activate.ps1
```

Infine, installiamo i requisiti del progetto
```sh
python3 -m pip install -r requirements.txt
```

Quindi, eseguiamo uno scenario nel simulatore realizzato:
```sh
python3 src/main.py maps/A.json -i num_iteration -t num_ticks -v (for verbose json)
```

## Help!
```sh
usage: main.py [-h] [-g] [-v] [-i ITERATIONS] [-t MAX_TICKS] mappa_json

Swarm Intelligence Simulator

positional arguments:
  mappa_json            Percorso del file JSON della mappa

options:
  -h, --help            show this help message and exit
  -g, --graphics        Attiva la visualizzazione grafica
  -v, --verbose         Salva lo storico dettagliato in JSON
  -i, --iterations ITERATIONS
                        Numero di simulazioni da eseguire
  -t, --max_ticks MAX_TICKS
                        Limite massimo di tick per run
```