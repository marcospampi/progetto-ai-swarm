import pandas as pd
import glob

df = pd.concat([pd.read_csv(f).assign(file=f) for f in glob.glob("*.csv")], ignore_index=True)
df['oggetti_recuperati'] = df['oggetti'].str.split('/').str[0].astype(int)

cols = ['oggetti_recuperati', 'ticks', 'energia_media_persa']
stats = df.groupby(['file', 'mappa'])[cols].agg(['mean', 'std', 'min', 'max']).round(2)

print(stats)