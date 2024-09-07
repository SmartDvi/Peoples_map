import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics import r2_score
import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import plotly.express as px
from pages.intro_dataset import extract_professions

dash.register_page(
    __name__,
    title='Geospatial Analysis',
    description='Geospatial Analysis',
    order=2
)

# Load the dataset
df = pd.read_csv('C:\\Users\\Moritus Peters\\Downloads\\people-map.csv')

# Initialize SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

# Extract profession and handle missing values
df['profession'] = df['extract'].apply(extract_professions)
df['extract'] = df['extract'].astype(str).fillna("")
df['sentiment'] = df['extract'].apply(lambda text: sia.polarity_scores(text)['compound'])
df.fillna({"lat": 0, "lng": 0, "views_median": 0, "views_sum": 0}, inplace=True)

# Define features and target for regression
X = df[['views_median']]  # You can add more features here
y = df['views_sum']

# Split the dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Add predicted values to the dataframe for visualization
df['predicted_views'] = model.predict(df[['views_median']])

# Define columns to display in the table
columns_to_display = ['name', 'city', 'views_sum', 'profession', 'predicted_views']

# defining color scale
red_blue_scale = px.colors.sequential.RdBu
red_blue_discrete = ['#FF0000', '#0000FF']

# Define the layout
layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(html.H5("Welcome to the Geospatial Analysis Page", className="text-center text-primary mb-4"), width=12)
        ]),
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='geo-graph', hoverData=None, config={'displayModeBar': False,  }, className='geo-map', style={'height': '400px', 'width': '100%'}),
               
            ),
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    dag.AgGrid(
                        id='table_detail',
                        columnDefs=[{'headerName': col, 'field': col} for col in columns_to_display],
                        rowData=df.to_dict('records'),
                        defaultColDef={'sortable': True, 'filter': True, 'resizable': True},
                        style={'height': '200px', 'width': '100%'},
                        className='ag-theme-alpine',
                        
                    )
                ),
              
            )
        )
 ])
    


# Define the callback for updating the map and the table
# Define the callback for updating the map and the table
@callback(
    Output('geo-graph', 'figure'),
    Output('table_detail', 'rowData'),
    Input('geo-graph', 'hoverData'),
    Input('table_detail', 'selectedRows')
)
def update_map_and_table(hoverData, selected_table_row):
    # Default to entire dataset
    filtered_df = df.copy()

    ## Handle hover data on the map
    if hoverData:
        hover_name = hoverData['points'][0]['hovertext']
        filtered_df = df[df['name'] == hover_name]

    # Handle hover or selection on the table
    elif selected_table_row:
        selected_name = selected_table_row[0]['name']
        filtered_df = df[df['name'] == selected_name]

    # Recalculate predictions if data is filtered
    if not filtered_df.empty:
        filtered_df['predicted_views'] = model.predict(filtered_df[['views_median']])


    # Create map figure showing the filtered data points
    fig = px.scatter_mapbox(
        df,  # Show all points on the map
        lat="lat",
        lon="lng",
        color="predicted_views",
        size="views_sum",
        hover_name="name",
        color_continuous_scale=red_blue_scale,
        hover_data={"views_sum": True, "sentiment": True, "profession": True, "city": True, "state": True},
        zoom=4.5,
        mapbox_style="open-street-map",
        title="Geospatial Visualization of Predicted Views"
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Update the table with the filtered data based on hover interaction (state-level filtering)
    return fig, filtered_df[columns_to_display].to_dict('records')
