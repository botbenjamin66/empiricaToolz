from createTool import dataFactory, yfinanceObject, fileDataObject
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import yfinance as yf
import dash

# FINANCIAL DATA
dfs = {}
dataObjects = {"msciValue": dataFactory().createData("file", "msciValue", "2023-01-01", "2023-11-24", "1d", "msciValue.xlsx", 8),
    "msciQuality": dataFactory().createData("file", "msciQuality", "2023-01-01", "2023-11-24", "1d", "msciQuality.xlsx", 8),
    "msciSmallcap": dataFactory().createData("file", "msciSmallcap", "2023-01-01", "2023-11-24", "1d", "msciSmallcap.xlsx", 8)}
for name, obj in dataObjects.items():
    df1 = obj.fetchData()
    df1.sort_index(ascending=True, inplace=True)
    df1 = df1.asfreq('B').ffill()
    dfs[name] = df1
df = pd.concat(dfs.values(), axis=1)
df.columns = dfs.keys()

# EVENT TIME SERIES
fedMoves = [
    ["2023-07-26", "+0.25%", "5.25%"],
    ["2023-05-03", "+0.25%", "5.00%"],
    ["2023-03-22", "+0.25%", "4.75%"],
    ["2023-02-01", "+0.25%", "4.50%"],
    ["2022-12-15", "+0.50%", "4.25%"],
    ["2022-11-02", "+0.75%", "3.75%"],
    ["2022-09-21", "+0.75%", "3.00%"],
    ["2022-07-27", "+0.75%", "2.25%"],
    ["2022-06-15", "+0.75%", "1.50%"],
    ["2022-05-04", "+0.50%", "0.75%"],
    ["2022-03-17", "+0.25%", "0.25%"],
    ["2020-03-16", "-1.00%", "0.00%"],
    ["2020-03-03", "-0.50%", "1.00%"],
    ["2019-10-31", "-0.25%", "1.50%"],
    ["2019-09-19", "-0.25%", "1.75%"],
    ["2019-08-01", "-0.25%", "2.00%"],
    ["2018-12-20", "+0.25%", "2.25%"],
    ["2018-09-27", "+0.25%", "2.00%"],
    ["2018-06-14", "+0.25%", "1.75%"],
    ["2018-03-22", "+0.25%", "1.50%"],
    ["2017-12-14", "+0.25%", "1.25%"],
    ["2017-06-15", "+0.25%", "1.00%"],
    ["2017-03-16", "+0.25%", "0.75%"],
    ["2016-12-15", "+0.25%", "0.50%"],
    ["2015-12-16", "+0.25%", "0.25%"],
    ["2008-12-16", "-1.00%", "0.00%"],
    ["2008-10-29", "-0.50%", "1.00%"],
    ["2008-10-08", "-0.50%", "1.50%"],
    ["2008-04-30", "-0.25%", "2.00%"],
    ["2008-03-18", "-0.75%", "2.25%"],
    ["2008-01-30", "-0.50%", "3.00%"],
    ["2008-01-22", "-0.75%", "3.50%"],
    ["2007-12-11", "-0.25%", "4.25%"],
    ["2007-10-31", "-0.25%", "4.50%"],
    ["2007-09-18", "-0.50%", "4.75%"],
    ["2006-06-29", "+0.25%", "5.25%"],
    ["2006-05-10", "+0.25%", "5.00%"],
    ["2006-03-28", "+0.25%", "4.75%"],
    ["2006-01-31", "+0.25%", "4.50%"],
    ["2005-12-13", "+0.25%", "4.25%"],
    ["2005-11-01", "+0.25%", "4.00%"],
    ["2005-09-20", "+0.25%", "3.75%"],
    ["2005-08-09", "+0.25%", "3.50%"],
    ["2005-06-30", "+0.25%", "3.25%"],
    ["2005-05-03", "+0.25%", "3.00%"],
    ["2005-03-22", "+0.25%", "2.75%"],
    ["2005-02-02", "+0.25%", "2.50%"],
    ["2004-12-14", "+0.25%", "2.25%"],
    ["2004-11-10", "+0.25%", "2.00%"],
    ["2004-09-21", "+0.25%", "1.75%"],
    ["2004-08-10", "+0.25%", "1.50%"],
    ["2004-06-30", "+0.25%", "1.25%"],
    ["2003-06-25", "-0.25%", "1.00%"],
    ["2002-11-06", "-0.50%", "1.25%"],
    ["2001-12-11", "-0.25%", "1.75%"],
    ["2001-11-06", "-0.50%", "2.00%"],
    ["2001-10-02", "-0.50%", "2.50%"],
    ["2001-09-17", "-0.50%", "3.00%"],
    ["2001-08-21", "-0.25%", "3.50%"],
    ["2001-06-27", "-0.25%", "3.75%"],
    ["2001-05-15", "-0.50%", "4.00%"],
    ["2001-04-18", "-0.50%", "4.50%"],
    ["2001-03-20", "-0.50%", "5.00%"],
    ["2001-01-31", "-0.50%", "5.50%"],
    ["2001-01-03", "-0.50%", "6.00%"],
    ["2000-05-16", "+0.50%", "6.50%"],
    ["2000-03-21", "+0.25%", "6.00%"],
    ["2000-02-02", "+0.25%", "5.75%"],
    ["1999-11-16", "+0.25%", "5.50%"],
    ["1999-08-24", "+0.25%", "5.25%"],
    ["1999-06-30", "+0.25%", "5.00%"],
    ["1998-11-17", "-0.25%", "4.75%"],
    ["1998-10-15", "-0.25%", "5.00%"],
    ["1998-09-29", "-0.25%", "5.25%"],
    ["1997-03-25", "+0.25%", "5.50%"],
    ["1996-01-31", "-0.25%", "5.25%"],
    ["1995-12-19", "-0.25%", "5.50%"],
    ["1995-07-06", "-0.25%", "5.75%"],
    ["1995-02-01", "+0.50%", "6.00%"],
    ["1994-11-15", "+0.75%", "5.50%"],
    ["1994-08-16", "+0.50%", "4.75%"],
    ["1994-05-17", "+0.50%", "4.25%"],
    ["1994-04-18", "+0.25%", "3.75%"],
    ["1994-03-22", "+0.25%", "3.50%"],
    ["1994-02-04", "+0.25%", "3.25%"],
    ["1992-09-04", "-0.25%", "3.00%"],
    ["1992-07-02", "-0.50%", "3.25%"],
    ["1992-04-09", "-0.25%", "3.75%"],
    ["1991-12-20", "-0.50%", "4.00%"],
    ["1991-12-06", "-0.25%", "4.50%"],
    ["1991-11-06", "-0.25%", "4.75%"],
    ["1991-10-31", "-0.25%", "5.00%"],
    ["1991-09-13", "-0.25%", "5.25%"],
    ["1991-08-06", "-0.25%", "5.50%"],
    ["1991-04-30", "-0.25%", "5.75%"],
    ["1991-03-08", "-0.25%", "6.00%"],
    ["1991-02-01", "-0.50%", "6.25%"],
    ["1991-01-09", "-0.25%", "6.75%"],
    ["1990-12-18", "-0.25%", "7.00%"],
    ["1990-12-07", "-0.25%", "7.25%"],
    ["1990-11-13", "-0.25%", "7.50%"],
    ["1990-10-29", "-0.25%", "7.75%"],
    ["1990-07-13", "-0.25%", "8.00%"]]
df2 = pd.DataFrame(fedMoves, columns=["Date", "Change", "Rate"])
df2["Date"] = pd.to_datetime(df2["Date"])
df2.set_index("Date", inplace=True)
df2["Action"] = df2["Change"].apply(lambda x: "Hike" if "+" in x else "Cut")
df2["Rate"] = df2["Rate"].str.rstrip('%').astype(float)
df2['Change'] = df2['Change'].str.rstrip('%').astype(float)
df2['policyChange'] = df2['Action'] != df2['Action'].shift(1)

# CONCATENATION
df = df.combine_first(df2)
df = df.asfreq('B').ffill()

# MORE DATA MANIPULATION
specifiedDate = pd.Timestamp('2023-01-01')
columnToAnalyze = 'Rate'
xDays = 10
returnsBeforeAndAfter = pd.concat([
    df[columnToAnalyze].pct_change().loc[specifiedDate - pd.Timedelta(days=xDays):specifiedDate],
    df[columnToAnalyze].pct_change().loc[specifiedDate:specifiedDate + pd.Timedelta(days=xDays)]]).dropna()

# VISUALIZATION
def createDashboard():
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Tabs([
            dcc.Tab(label='Main Dashboard', children=[
                html.Div([
                    html.H1("Data Visualization Dashboard", style={'textAlign': 'center', 'color': '#1E1E1E'}),
                    dcc.Dropdown(
                        id='column-dropdown',
                        options=[{'label': col, 'value': col} for col in df.columns],
                        value=df.columns[0],
                        style={'width': '50%', 'margin': 'auto'}
                    ),
                    dcc.Graph(id='data-graph')
                ], style={'backgroundColor': '#F2F2F2'})
            ]),
            dcc.Tab(label='Price Chart', children=[
                html.Div([
                    html.H1("Price Chart", style={'textAlign': 'center', 'color': '#1E1E1E'}),
                    html.Div([
                        html.Label('Choose a Date from df2:', style={'color': '#1E1E1E'}),
                        dcc.Dropdown(
                            id='dropdown-date-df2',
                            options=[{'label': str(date), 'value': str(date)} for date in df2.index],
                            value=str(df2.index[0]),
                            style={'width': '50%', 'margin': 'auto'}
                        ),
                        html.Label('Enter Number of Days (xDays):', style={'color': '#1E1E1E'}),
                        dcc.Input(id='input-xdays', type='number', value=10, style={'width': '50%', 'margin': 'auto'}),
                        html.Label('Select Columns from df:', style={'color': '#1E1E1E'}),
                        dcc.Dropdown(
                            id='column-selection',
                            options=[{'label': col, 'value': col} for col in df.columns],
                            multi=True,
                            value=[df.columns[0]],
                            style={'width': '50%', 'margin': 'auto'}
                        ),
                    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
                    dcc.Graph(id='price-chart')
                ], style={'backgroundColor': '#F2F2F2'})
            ])
        ])
    ], style={'fontFamily': 'Arial, sans-serif'})

    @app.callback(
        Output('data-graph', 'figure'),
        [Input('column-dropdown', 'value')])
    def update_main_graph(selected_column):
        fig = px.line(df, y=selected_column)
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        return fig

    @app.callback(
        Output('price-chart', 'figure'),
        [Input('dropdown-date-df2', 'value'), Input('input-xdays', 'value'), Input('column-selection', 'value')]
    )
    def update_chart(dropdown_date_df2, input_xdays, column_selection):
        fig = go.Figure()
        specified_date = pd.Timestamp(dropdown_date_df2)
        x_days = input_xdays

        for column in column_selection:
            returns = pd.concat([
                df[column].pct_change().loc[specified_date - pd.Timedelta(days=x_days):specified_date],
                df[column].pct_change().loc[specified_date:specified_date + pd.Timedelta(days=x_days)]
            ]).dropna()
            fig.add_trace(go.Scatter(x=returns.index, y=returns, mode='lines', name=column))

        fig.update_layout(title=f'Price Chart for Selected Columns', xaxis_title='Date', xaxis=dict(tickformat='%Y-%m-%d'))
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        return fig

    if __name__ == '__main__':
        app.run_server(debug=True)


if __name__ == '__main__':
    createDashboard()