# Importing necessary libraries for web scraping
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the Wikipedia page for S&P 500 companies
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def updateStocks():
    # Send a request to fetch the content of the page
    response = requests.get(url)

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the first table in the page that contains the list of S&P 500 companies
    table = soup.find('table', {'id': 'constituents'})

    # Extract the table headers
    headers = [header.text.strip() for header in table.find_all('th')]

    # Extract the table rows
    rows = []
    for row in table.find_all('tr')[1:]:
        rows.append([cell.text.strip() for cell in row.find_all('td')])

    # Create a DataFrame from the extracted data
    df_sp500 = pd.DataFrame(rows, columns=headers)
    df_sp500.columns = ['Company','Sector','Sub-Industry','Headquarters','Location', 'Date added','CIK','Founded']
    print('stocks listed')

    # Display the first few rows of the DataFrame
    if not os.path.exists('./data/SP500 list stocks.csv'):
        with open('./data/SP500 list stocks.csv', 'w'): pass

    df_sp500.to_csv('./data/SP500 list stocks.csv')
    print('stocks updated')
