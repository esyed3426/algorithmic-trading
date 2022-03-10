# Ehsan Syed
# March 9 2022
# Algorithmic Trading - Equal Weight S&P 500 Screener

# This project takes in the value of a portfolio and returns the
# amount of shares of each S&P 500 company to buy (or not buy)

'''----------------------------------------------------------------'''

# Import libraries


# Pandas makes working with tabular data in Python much easier
# using its custom "DataFrame"
# ie. Data with rows and columns
import pandas as pd

# Requests makes our GET requests (HTTP Requests) helps us interact
# with the API
import requests

# XLSX Writer helps save formatted xlsx files from Python scripts
import xlsxwriter

# Math helps with basic operations
import math

'''----------------------------------------------------------------'''

# IMPORTING THE LIST OF STOCKS
# (Normally this part would directly connect to an API
# but that costs money)

# Read data from the csv into a new Pandas DataFrame
stocks = pd.read_csv('sp_500_stocks.csv')

'''----------------------------------------------------------------'''

# Importing our (Sandbox) API Token from the secrets file
# Sandbox --> Randomized Data usually used for testing
# Note: When adding a file to the working directory of a Jupyter Notebook
# restart the kernel and run all cells to fix
# Follow up: No longer necessary when working with pure Python files

from secrets import IEX_CLOUD_API_TOKEN

'''----------------------------------------------------------------'''

# Structuring our first API Call to the IEX_CLOUD
# We use the 'quote' endpoint to get the market cap and price of each stock

symbol = 'AAPL'
api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data = requests.get(api_url).json()

'''----------------------------------------------------------------'''

# Parsing the API Call to get market cap and price

price = data['latestPrice']
market_cap = data['marketCap']

'''----------------------------------------------------------------'''

# Example of adding stock to a Pandas DataFrame ('spreadsheet')

my_columns = ['Ticker', 'Price','Market Capitalization', 'Number Of Shares to Buy']
final_dataframe = pd.DataFrame(columns = my_columns)

# Use Pandas series for the rows

final_dataframe = final_dataframe.append(
                    pd.Series(['AAPL', 
                                data['latestPrice'], 
                                data['marketCap'], 
                                'N/A'], # We don't know how many to buy just yet
                    index = my_columns), 
                ignore_index = True)


'''----------------------------------------------------------------'''

# Using the same method as above, loop through the tickers and overwrite
# the current Pandas DataFrame

for symbol in stocks['ticker']:
    api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(api_url).json()
    final_dataframe = final_dataframe.append(
                                        pd.Series([symbol, 
                                                   data['latestPrice'], 
                                                   data['marketCap'], 
                                                   'N/A'], 
                                                  index = my_columns), 
                                        ignore_index = True)


'''----------------------------------------------------------------'''

# Speeding up performance by using batch API calls
# We have to split up the list into chunks of 100 each

'''
# This is a function I created on my own
# Worst case behaviour is O(n) when n == 1
# Since the project uses the other function, this is just for my own knowledge
# chunks: (listof X) Nat -> (listof (listof X)) 
def chunks(lst, n):

    length = len(lst)

    # Determine how many chunks there will be
    num_chunks = math.ceil(length / n)
    return_values = [0] * num_chunks

    start_index = 0
    for i in range(0, num_chunks):
        if (i == num_chunks - 1 and start_index + n > length):
            return_values[i] = lst[start_index: length]
        else:
            return_values[i] = lst[start_index: start_index + n]
            start_index += n
    return return_values 
'''

# Function sourced from 
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
                                        pd.Series([symbol, 
                                                   data[symbol]['quote']['latestPrice'], 
                                                   data[symbol]['quote']['marketCap'], 
                                                   'N/A'], 
                                                  index = my_columns), 
                                        ignore_index = True)

    
'''----------------------------------------------------------------'''

# Take in the value of a user's portfolio and calculate the amount of shares to buy
# Type check at the same time

def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")

portfolio_input()


# Calculate the amount of shares to buy using floor division

position_size = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])-1):
    final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
final_dataframe

'''----------------------------------------------------------------'''

# Initialize the XLSX Writer object

writer = pd.ExcelWriter('recommended_trades.xlsx', engine = 'xlsxwriter')
final_dataframe.to_excel(writer, sheet_name = "Recommended Trades", index = False)

'''----------------------------------------------------------------'''

# Creating the formats needed for the xlsx file
# We need
# String format for tickers
# $XX.XX format for stock prices
# $XX,XXX format for market capitalization
# Integer format for the number of shares to purchase

background_color = '#0a0a23'
font_color = '#ffffff'

string_format = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

dollar_format = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

integer_format = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

'''----------------------------------------------------------------'''

# Now, we apply formats to columns of the xlsx file to be exported

column_formats = { 
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Market Capitalization', dollar_format],
                    'D': ['Number of Shares to Buy', integer_format]
                    }

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

writer.save()