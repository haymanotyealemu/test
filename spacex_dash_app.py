import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Dropdown for Launch Site selection
                                html.Div(dcc.Dropdown(id='site-dropdown', 
                                                      options=[
                                                          {'label': 'All Sites', 'value': 'ALL'},
                                                          {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                          {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                          {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                          {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                                      ],
                                                      value='ALL',  # Default value
                                                      placeholder="Select a Launch Site here",
                                                      searchable=True)),
                                
                                # Graph to display the pie chart
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                
                                html.Br(),

                                # Payload range slider
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, 
                                                max=10000, 
                                                step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # Scatter plot for payload vs. success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Callback for the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df.groupby('Launch Site')['class'].sum()
        fig = px.pie(success_counts, values='class',names=success_counts.index,title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        fig = px.pie(success_fail_counts, values='count',names=success_fail_counts.index,title=f'Total Success launches for site {entered_site}')
    return fig
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {entered_site}')
    return fig
# Run the app
if __name__ == '__main__':
    app.run_server()


