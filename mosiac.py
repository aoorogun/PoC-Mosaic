import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output
from dash import dash_table

# Step 1: Data Preparation
df = pd.read_csv('/Users/aoamacsplace/Documents/mosaic/py viz/simple.csv')

# Step 2: Dashboard Layout
app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1('Optimism Airdrop Criteria'),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Label('Select Columns'),
                        dcc.Dropdown(
                            id='column-selector',
                            options=[{'label': col, 'value': col} for col in df.columns],
                            multi=True,
                            placeholder='Select columns...'
                        )
                    ],
                    className='column-selector'
                ),
                html.Div(
                    children=[
                        html.Label('Analysis Options'),
                        dcc.RadioItems(
                            id='analysis-option',
                            options=[
                                {'label': 'Descriptive Statistics', 'value': 'descriptive'},
                                {'label': 'Top N Values', 'value': 'top_n'},
                                {'label': 'Bottom N Values', 'value': 'bottom_n'}
                            ],
                            value='descriptive',
                            labelStyle={'display': 'block'}
                        )
                    ],
                    className='analysis-options'
                ),
                html.Div(
                    children=[
                        html.Label('Value Filter'),
                        dcc.Input(
                            id='value-filter',
                            type='number',
                            placeholder='Enter a value...'
                        )
                    ],
                    className='value-filter'
                )
            ],
            className='controls-container'
        ),

        html.Hr(),

        html.Div(
            children=[
                dash_table.DataTable(
                    id='output-table',
                    style_cell={'textAlign': 'left'},
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    }
                ),
                dcc.Graph(id='output-chart')
            ],
            className='output-container'
        )
    ],
    className='container'
)

# Step 3: Data Analysis
def analyze_data(df, columns, analysis_option, value_filter):
    if analysis_option == 'descriptive':
        return df[columns].describe().reset_index().to_dict('records')
    elif analysis_option == 'top_n':
        return df.nlargest(value_filter, columns).to_dict('records')
    elif analysis_option == 'bottom_n':
        return df.nsmallest(value_filter, columns).to_dict('records')

def plot_chart(df, x_column, y_column):
    fig = px.bar(df, x=x_column, y=y_column, title='Airdrop Criteria Analysis')
    fig.update_layout(yaxis=dict(title='Count'), margin=dict(b=100))
    return fig

# Step 4: Callback Functions
@app.callback(
    Output('output-table', 'data'),
    Output('output-table', 'columns'),
    Output('output-chart', 'figure'),
    Input('column-selector', 'value'),
    Input('analysis-option', 'value'),
    Input('value-filter', 'value')
)
def update_output(columns, analysis_option, value_filter):
    if columns and analysis_option and value_filter:
        data = analyze_data(df, columns, analysis_option, value_filter)
        if len(columns) >= 2:
            chart = plot_chart(df, columns[0], columns[1])
        else:
            chart = None

        # Update the table to show the ENS name instead of NaN
        if 'ens_name' in columns:
            df_ens = df[['address', 'ens_name']].dropna(subset=['ens_name'])
            df_ens.columns = ['address', 'ens_name']
            data = pd.merge(data, df_ens, on='address', how='left')

        return data, [{"name": col, "id": col} for col in data[0].keys()], chart

    return [], [], None

# Step 5: Run the Dashboard
# server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
