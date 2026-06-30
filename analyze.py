import pandas as pd 
import sqlite3 as sql
import matplotlib.pyplot as plt

conncect = sql.connect('searches.db')
df = pd.read_sql('SELECT * FROM searches', conncect)
print(df)
print(df['temperature'].mean()) 
print(df.sort_values('temperature', ascending=False))
print(df['country'].value_counts())

df.plot(x='country', y=['temperature', 'humidity', ''], kind='bar')
plt.show()