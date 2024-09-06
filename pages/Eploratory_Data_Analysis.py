import pandas as pd
import numpy as np
import re
import plotly.express as px
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc



dash.register_page(
     __name__,
    title='Exploratory Data Analysis',
    description= 'A bit insight about the dataset',
    order=1
   
)

# Initialize SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

# reading and loading  the dataset
df = pd.read_csv('C:\\Users\\Moritus Peters\\Downloads\\people-map.csv')

# Handle missing values and convert non-string values to string
df['extract'] = df['extract'].astype(str).fillna("")

# Apply sentiment analysis
df['sentiment'] = df['extract'].apply(lambda text: sia.polarity_scores(text)['compound'])

# renaming the lat and lng
if 'lat' in df.columns and 'lng' in df.columns:
    df.rename(columns={'lat': 'latitude', 'lng': 'longitude'}, inplace=True)

# Convert 'views_median' and 'views_sum' to numeric, handling errors
df['views_median'] = pd.to_numeric(df['views_median'], errors='coerce')
df['views_sum'] = pd.to_numeric(df['views_sum'], errors='coerce')

# Drop rows with missing values in important columns
df.dropna(subset=['latitude', 'longitude', 'views_median', 'views_sum', 'state', 'city'], inplace=True)

# removing extract space in the state and city
df['state'] = df['state'].str.strip()
df['city'] = df['city'].str.strip()

# Aggregate data by state
state_agg = df.groupby('state').agg(
    total_views_sum=('views_sum', 'sum'),
    total_views_median=('views_median', 'median'),
    average_sentiment=('sentiment', 'mean'),
    count=('views_sum', 'count')
).reset_index()

# Aggregate data by city
city_agg = df.groupby(['state', 'city', 'latitude', 'longitude']).agg(
    total_views_sum=('views_sum', 'sum'),
    total_views_median=('views_median', 'median'),
    average_sentiment=('sentiment', 'mean'),
    count=('views_sum', 'count')
).reset_index()

# Create a dictionary for state abbreviations using the first two letters
#us_state_abbrev = {state: state[:2].upper() for state in df.state}
us_state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA',
    'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
    'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
# Map state names to abbreviations
state_agg['state_code'] = state_agg['state'].map(us_state_abbrev)

# Handle any states not in the mapping
state_agg['state_code'].fillna(state_agg['state'], inplace=True)

red_blue_scale = px.colors.sequential.RdBu
red_blue_discrete = ['#FF0000', '#0000FF']



# Define the layout of the app
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H5(" Welcome To Data Exploratory Analysis Page", className="text-center text-primary, mb-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select View Type:"),
            dcc.Dropdown(
                id='view-type-dropdown',
                options=[
                    {'label': 'Total Views Sum', 'value': 'total_views_sum'},
                    {'label': 'Median Views', 'value': 'total_views_median'}
                ],
                value='total_views_sum',
                clearable=False
            )
        ], width=6),
        
        dbc.Col([
            html.Label("Select Geographic Level:"),
            dcc.Dropdown(
                id='geo-level-dropdown',
                options=[
                    {'label': 'State', 'value': 'state'},
                    {'label': 'City', 'value': 'city'}
                ],
                value='state',
                clearable=False
            )
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='choropleth-map')
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select Top N:"),
            dcc.Slider(
                id='top-n-slider',
                min=5,
                max=20,
                step=1,
                value=10,
                marks={i: str(i) for i in range(5, 21, 5)}
            ),
            dcc.Graph(id='top-n-bar-chart')
        ], width=6),
        
        dbc.Col([
            html.Label("Select State for City Analysis:"),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': state, 'value': state} for state in sorted(df['state'].unique())],
                value=df['state'].unique()[0],
                clearable=False
            ),
            dcc.Graph(id='top-cities-bar-chart')
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='views-box-plot')
        ], width=12)
    ]),
    
   
], fluid=True)

# Callback to update the choropleth map
@callback(
    Output('choropleth-map', 'figure'),
    Input('view-type-dropdown', 'value'),
    Input('geo-level-dropdown', 'value')
)
def update_choropleth(view_type, geo_level):
    if geo_level == 'state':
        fig = px.choropleth(
            state_agg,
            locations='state_code',
            locationmode="USA-states",
            color=view_type,
            scope="usa",
            hover_data=['state', view_type],
            color_continuous_scale=red_blue_scale,
            labels={view_type: "Views"}
        )
        fig.update_layout(title_text=f'Views by State ({view_type.replace("_", " ").title()})')
    else:
        # For cities, use a scatter plot on a map
        fig = px.scatter_mapbox(
            city_agg,
            lat='latitude',
            lon='longitude',
            size=view_type,
            color=view_type,
            hover_name='city',
            hover_data=['state', view_type],
            color_continuous_scale=red_blue_scale,
            size_max=15,
            zoom=3,
            mapbox_style="carto-positron",
            title=f'Views by City ({view_type.replace("_", " ").title()})'
        )
    return fig

# Callback to update the top N bar chart
@callback(
    Output('top-n-bar-chart', 'figure'),

    Input('view-type-dropdown', 'value'),
    Input('geo-level-dropdown', 'value'),
    Input('top-n-slider', 'value')
)
def update_top_n_bar(view_type, geo_level, top_n):
    if geo_level == 'state':
        data = state_agg.sort_values(by=view_type, ascending=False).head(top_n)
        fig = px.bar(
            data,
            x=view_type,
            y='state',
            orientation='h',
            title=f'Top {top_n} States by {view_type.replace("_", " ").title()}',
            labels={view_type: "Views", 'state': "State"},
            color=view_type,
            color_continuous_scale=red_blue_scale,
            #text='total_views_sum'
        )
    else:
        # For cities, aggregate views and sort
        data = city_agg.sort_values(by=view_type, ascending=False).head(top_n)
        fig = px.bar(
            data,
            x=view_type,
            y='city',
            orientation='h',
            title=f'Top {top_n} Cities by {view_type.replace("_", " ").title()}',
            labels={view_type: "Views", 'city': "City"},
            color=view_type,
            color_continuous_scale=red_blue_scale,
            #text='total_views_sum'
        )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

# Callback to update the top cities bar chart based on selected state
@callback(
    Output('top-cities-bar-chart', 'figure'),
    Input('view-type-dropdown', 'value'),
    Input('state-dropdown', 'value'),
    Input('top-n-slider', 'value')
)
def update_top_cities_bar(view_type, selected_state, top_n):
    filtered_cities = city_agg[city_agg['state'] == selected_state]
    data = filtered_cities.sort_values(by=view_type, ascending=False).head(top_n)
    fig = px.bar(
        data,
        x=view_type,
        y='city',
        orientation='h',
        title=f'Top {top_n} Cities in {selected_state} by {view_type.replace("_", " ").title()}',
        labels={view_type: "Views", 'city': "City"},
        color=view_type,
        color_continuous_scale=red_blue_scale
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

# Callback to update the views box plot
@callback(
    Output('views-box-plot', 'figure'),
    Input('geo-level-dropdown', 'value')
)
def update_box_plot(geo_level):
    if geo_level == 'state':
        fig = px.box(
            state_agg,
            y='total_views_sum',
            x='state',
            title='Distribution of Total Views Sum by State',
            labels={'total_views_sum': 'Total Views Sum', 'state': 'State'},
            points='all'
        )
    else:
        fig = px.box(
            city_agg,
            y='total_views_sum',
            x='state',
            title='Distribution of Total Views Sum by State (Aggregated over Cities)',
            labels={'total_views_sum': 'Total Views Sum', 'state': 'State'},
            points='all'
        )
    fig.update_layout(showlegend=False)
    return fig