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
