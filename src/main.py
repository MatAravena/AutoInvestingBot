import webscrapping as wb
import pandas as pd

wb.updateStocks()

df = pd.read_csv('./data/SP500 list stocks.csv', index_col=0)




