import pandas as pd
import os
from rich.table import Table

class Logger_csv:
    def __init__(self, filename="results/risultati_run.csv"):
        self.filename = filename
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

    def log_run(self, dati_run, console=None):
        df = pd.DataFrame([dati_run])
        hdr = not os.path.isfile(self.filename)
        df.to_csv(self.filename, mode='a', index=False, header=hdr)
        
        if console:
            table = Table(title="Risultati Simulazione", header_style="bold magenta")
            table.add_column("Metrica")
            table.add_column("Valore", justify="right")
            for k, v in dati_run.items():
                table.add_row(k.replace('_', ' ').title(), str(v))
            console.print(table)