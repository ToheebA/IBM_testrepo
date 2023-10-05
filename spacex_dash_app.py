# Import required libraries
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
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # Modified Dropdown with custom CSS
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='ALL',  # Default value is 'ALL'
        style={'width': '100%'}  # Set width to 100% for full page
    ),
    html.Br(),
    
    # Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    # Modified payload range slider with step size of 2500kg
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=2500,  # Set step size to 2500kg
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[0, 10000]
    ),
    
    # Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Calculate successful launches percentage for each site
        success_percentages = []

        for site in spacex_df['Launch Site'].unique():
            site_data = spacex_df[spacex_df['Launch Site'] == site]
            total_launches = len(site_data)
            successful_launches = len(site_data[site_data['class'] == 1])
            success_percentage = (successful_launches / total_launches) * 100
            success_percentages.append({'Site': site, 'Success Percentage': success_percentage})

        success_percentages_df = pd.DataFrame(success_percentages)
        fig = px.pie(
            success_percentages_df,
            names='Site',
            values='Success Percentage',
            title='Total Success Launches By Site'
        )
    else:
        # Filter data for specific site
        filtered_data = spacex_df[spacex_df['Launch Site'] == selected_site]

        # Calculate successful and failed counts
        success_count = len(filtered_data[filtered_data['class'] == 1])
        failed_count = len(filtered_data[filtered_data['class'] == 0])

        # Create pie chart figure
        fig = px.pie(
            names=['Successful', 'Failed'],
            values=[success_count, failed_count],
            title=f'Successful vs. Failed Launches ({selected_site})'
        )

    return fig

# Callback for scatter chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        # Filter data for all sites within selected payload range
        filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                  (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        # Filter data for specific site within selected payload range
        filtered_data = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                  (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                  (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    # Create scatter chart figure
    fig = px.scatter(
        filtered_data,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Correlation between Payload and Success for {selected_site}'
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
