
# NEW WIKI DATA MUST BE CLEARED BY HAND FROM " " VIA EXCEL
import pandas as pd
import numpy as np
import time
import glob
import os
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

### VARIABLES & DICTIONARIES
trail1 = 50

### FUNCTIONS
def df():
    downloadsPath = os.path.expanduser('~/Downloads')
    filePaths = [file for file in sorted(glob.glob(f"{downloadsPath}/W*.csv"), key=os.path.getmtime, reverse=True)]
    latestFiles = filePaths[:2]

    # PRICE DATA
    if latestFiles:
        dfPrice = pd.read_csv(latestFiles[1], sep=';', decimal=',', thousands='.', engine='python', encoding='latin1', skiprows=5)
        dfPrice.drop(dfPrice.columns[1], axis=1, inplace=True)
        dfPrice['Date'] = pd.to_datetime(dfPrice.iloc[:, 0].str[:10], format='%d.%m.%Y')
        dfPrice['Time'] = dfPrice.iloc[:, 0].str[10:].str.strip()
        dfPrice.set_index('Date', inplace=True)
        dfPrice.drop(dfPrice.columns[0], axis=1, inplace=True)
        dfPrice.drop(columns=['Time'], inplace=True)
 
    # TRANSACTION DATA
    if len(latestFiles) > 1:
        dfTransactions = pd.read_csv(latestFiles[0], sep=';', decimal=',', thousands='.', engine='python', encoding='latin1', skiprows=5)
        dfTransactions['Date'] = pd.to_datetime(dfTransactions.iloc[:, 0].str[:10], format='%d.%m.%Y')
        dfTransactions['Time'] = dfTransactions.iloc[:, 0].str[10:].str.strip()
        dfTransactions.set_index('Date', inplace=True)

        # CUTOFF DATE
        cutOffDate = pd.to_datetime('01.01.2022', format='%d.%m.%Y')
        dfTransactions = dfTransactions[dfTransactions.index >= cutOffDate]
        dfTransactions.drop(dfTransactions.columns[0], axis=1, inplace=True)
        dfTransactions.insert(0, 'Time', dfTransactions.pop('Time'))

        # RENAME COLUMNS
        transaction_types = ['Wertpapier-Transaktion(Verkauf)', 'Wertpapier-Transaktion(Kauf)']
        dfTransactions = dfTransactions[dfTransactions['Beschreibung'].isin(transaction_types)].replace({
            'Wertpapier-Transaktion(Kauf)': 'buy', 'Wertpapier-Transaktion(Verkauf)': 'sell'}).rename(
            columns={'ÄnderungAnzahl': 'deltaContracts', 'Anzahlnachher': 'Contracts', 'Preis': 'Price', 
                    'ÄnderungCash': 'deltaCash', 'Cashnachher': 'Cash'}).filter(regex='^(?!.*Brutto).*$')

        # TRADES PER ISIN
        dfTransactions.sort_values(by=['ISIN', 'Date'], inplace=True)
        dfTransactions['Account'] = dfTransactions.groupby('ISIN')['deltaContracts'].cumsum()
        td = dfTransactions
        isNewIsin = (td['ISIN'] != td['ISIN'].shift()).astype(bool)
        wasAccountZero = (td['Account'].shift() == 0).astype(bool)
        resetTrade = isNewIsin | wasAccountZero
        groupKeys = resetTrade.cumsum()
        td['Trades'] = td.groupby(groupKeys).cumcount() + 1

        # INDEX MAP ALPACA
        dfTransactions['Alpaca'] = dfTransactions.index.map(dfPrice['Close'])
        dfTransactions['Alpaca'].fillna(method='ffill', inplace=True)
        dfTransactions['Exposure'] = 1 - ((dfTransactions['Cash'] / 1000) / dfTransactions['Alpaca'])
        dfTransactions['tradeSize'] = (dfTransactions['deltaCash'] / 1000) / dfTransactions['Alpaca']

        # COST BASIS
        dfTransactions.reset_index(drop=False, inplace=True)
        dfTransactions['costBasis'] = np.nan
        dfTransactions.loc[dfTransactions['Trades'] == 1, 'costBasis'] = dfTransactions['Price']
        for i, row in dfTransactions.iterrows():
            if row['Trades'] != 1:
                change_amount = row['deltaContracts']
                amount_after = row['Contracts']
                if row['deltaCash'] < 0 and amount_after != 0:
                    dfTransactions.at[i, 'costBasis'] = (
                        row['Price'] * (change_amount / amount_after) +
                        dfTransactions.at[i - 1, 'costBasis'] * (1 - (change_amount / amount_after)))
                elif i > 0:
                    dfTransactions.at[i, 'costBasis'] = dfTransactions.at[i - 1, 'costBasis']

        # RETURNS
        dfTransactions['percReturnTrade'] = np.where(dfTransactions['deltaCash'] > 0, (dfTransactions['Price'] - dfTransactions['costBasis']) / dfTransactions['costBasis'], np.nan)
        dfTransactions['totalReturnPf'] = dfTransactions['percReturnTrade'] * (dfTransactions['deltaCash'] / (dfTransactions['Alpaca'] * 100))
        dfTransactions.set_index('Date', inplace=True)
        dfTransactions = dfTransactions.iloc[::-1]
        
        # STATS
        #dfTransactions['Win'] = 1
        #dfTransactions['Loss'] = 2
        #dfTransactions['HitRate'] = dfTransactions['Win'].rolling(window=len(dfTransactions)).mean()
        #dfTransactions['ExpValue'] = dfTransactions['totalReturnPf'].rolling(window=len(dfTransactions)).mean()
        #dfTransactions['Turnover'] = dfTransactions['deltaCash'].abs().cumsum()
        #dfTransactions['RollingAvgWins'] = dfTransactions['Win'].rolling(window=30).mean()  # Example for a 30-day window


        return dfPrice, dfTransactions

### MAIN
dfPrice, dfTransactions = df()

def createDashboardTransactions(dfPrice, dfTransactions):
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1('Hedge Fund Dashboard', style={'textAlign': 'center', 'color': 'navy', 'margin-top': '20px'}),
        
        dcc.Tabs(id='tabs', value='price-tab', children=[
            dcc.Tab(label='Price Data', value='price-tab', style={'background-color': 'lightblue', 'color': 'navy'}),
            dcc.Tab(label='Transaction Data', value='transaction-tab', style={'background-color': 'lightblue', 'color': 'navy'}),
            dcc.Tab(label='Statistics', value='stats-tab', style={'background-color': 'lightblue', 'color': 'navy'}),
        ]),
        
        html.Div(id='tab-content')
    ], style={'background-color': 'beige'})

    @app.callback(
        Output('tab-content', 'children'),
        Input('tabs', 'value')
    )
    def render_content(tab):
        if tab == 'price-tab':
            price_fig = go.Figure()
            price_fig.add_trace(go.Scatter(x=dfPrice.index, y=dfPrice['Close'], mode='lines', name='Price', line=dict(color='navy')))
            price_fig.update_layout(title='Price Data', xaxis_title='Date', yaxis_title='Price', template='plotly_dark')
            return dcc.Graph(figure=price_fig)

        elif tab == 'transaction-tab':
            transaction_fig1 = go.Figure()
            transaction_fig1.add_trace(go.Scatter(x=dfTransactions.index, y=dfTransactions['Alpaca'], mode='lines', name='Alpaca', line=dict(color='lightblue')))
            transaction_fig1.update_layout(title='Alpaca', xaxis_title='Date', yaxis_title='Value', template='plotly_dark')
            
            transaction_fig2 = go.Figure()
            transaction_fig2.add_trace(go.Scatter(x=dfTransactions.index, y=dfTransactions['Exposure'], mode='lines', name='Exposure', line=dict(color='beige')))
            transaction_fig2.update_layout(title='Exposure', xaxis_title='Date', yaxis_title='Value', template='plotly_dark')
            
            transaction_fig3 = go.Figure()
            transaction_fig3.add_trace(go.Scatter(x=dfTransactions.index, y=dfTransactions['tradeSize'], mode='lines', name='Trade Size', line=dict(color='yellow')))
            transaction_fig3.update_layout(title='Trade Size', xaxis_title='Date', yaxis_title='Value', template='plotly_dark')
            
            transaction_fig4 = go.Figure()
            transaction_fig4.add_trace(go.Scatter(x=dfTransactions.index, y=dfTransactions['percReturnTrade'], mode='lines', name='Percentage Return', line=dict(color='brown')))
            transaction_fig4.update_layout(title='Percentage Return', xaxis_title='Date', yaxis_title='Value', template='plotly_dark')
            
            transaction_fig5 = go.Figure()
            transaction_fig5.add_trace(go.Scatter(x=dfTransactions.index, y=dfTransactions['totalReturnPf'], mode='lines', name='Total Return', line=dict(color='navy')))
            transaction_fig5.update_layout(title='Total Return', xaxis_title='Date', yaxis_title='Value', template='plotly_dark')
            
            return html.Div([
                dcc.Graph(figure=transaction_fig1),
                dcc.Graph(figure=transaction_fig2),
                dcc.Graph(figure=transaction_fig3),
                dcc.Graph(figure=transaction_fig4),
                dcc.Graph(figure=transaction_fig5)
            ])

        elif tab == 'stats-tab':
            stats_table = html.Table(
                [html.Tr([html.Td('Stat 1', style={'color': 'navy'}), html.Td('Value 1', style={'color': 'navy'})]),
                 html.Tr([html.Td('Stat 2', style={'color': 'navy'}), html.Td('Value 2', style={'color': 'navy'})])],
                style={'width': '50%', 'margin': 'auto', 'background-color': 'beige'}
            )
            return stats_table

    app.run_server(debug=True)

# Usage example:
createDashboardTransactions(dfPrice, dfTransactions)

# stats, rollingStats (wins, losses, hitRate, expValue, holdingPeriod, turnover)
# loopStorer: get ticker, buy date, prices, %after buy - last buy sell win loss charts
# sdax add

# dash
