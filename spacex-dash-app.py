# spacex-dash-app.py
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the SpaceX dataset
spacex_df = pd.read_csv('spacex_launch_dash.csv')

# Standardize column names
spacex_df.columns = [col.strip().lower() for col in spacex_df.columns]

# Filter only Falcon 9 launches
spacex_df = spacex_df[spacex_df['booster version'] != 'Falcon 1']

# Get min and max payload for slider
min_payload = spacex_df['payload mass (kg)'].min()
max_payload = spacex_df['payload mass (kg)'].max()

# Create Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Task 1: Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['launch site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # Task 2: Pie chart for success counts
    dcc.Graph(id='success-pie-chart'),

    html.Br(),

    html.P("Payload range (Kg):"),

    # Task 3: Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Task 4: Scatter chart for success vs payload
    dcc.Graph(id='success-payload-scatter-chart'),
])

# Task 2: Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='launch site',
            values='class',
            title='Total Success Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['launch site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(
            success_counts,
            names='class',
            values='count',
            title=f'Success vs Failure for site {entered_site}'
        )
    return fig

# Task 4: Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['payload mass (kg)'] >= low) & (spacex_df['payload mass (kg)'] <= high)

    if entered_site == 'ALL':
        filtered_df = spacex_df[mask]
        title = 'Payload vs. Outcome for All Sites'
    else:
        filtered_df = spacex_df[(spacex_df['launch site'] == entered_site) & mask]
        title = f'Payload vs. Outcome for site {entered_site}'

    fig = px.scatter(
        filtered_df,
        x='payload mass (kg)',
        y='class',
        color='booster version category',
        title=title,
        hover_data=['launch site', 'booster version']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
