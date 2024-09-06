import dash
import pandas as pd
import dash_ag_grid as dag
import re
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback


dash.register_page(
     __name__,
    path='/',
    title='Introducto and Dataset Details',
    description= 'Belief Intoduction to the project and Dateset details',
    order=0
   
)

# Load the dataset
df = pd.read_csv('C:\\Users\\Moritus Peters\\Downloads\\people-map.csv')

# Define a list of common professions (you can expand this list)
professions = ['Actor', 'Actress', 'Singer', 'Musician', 'Politician', 'Businessman', 'Businesswoman', 'Athlete', 
    'Footballer', 'Basketball Player', 'Wrestler', 'Boxer', 'UFC Fighter', 'Cricketer', 'Golfer', 
    'Tennis Player', 'Baseball Player', 'Coach', 'Referee', 'President', 'Vice President', 'Senator', 
    'Representative', 'Lawyer', 'Judge', 'Journalist', 'News Anchor', 'Reporter', 'Professor', 
    'Teacher', 'Scientist', 'Engineer', 'Doctor', 'Nurse', 'Surgeon', 'Psychologist', 'Therapist', 
    'Comedian', 'Writer', 'Author', 'Director', 'Producer', 'Screenwriter', 'Entrepreneur', 'Investor', 
    'Consultant', 'Real Estate Agent', 'Pilot', 'Soldier', 'Navy Officer', 'Air Force Officer', 
    'Astronaut', 'Model', 'Influencer', 'YouTuber', 'Dancer', 'Painter', 'Sculptor', 'Architect', 
    'Designer', 'Photographer', 'Chef', 'Fashion Designer', 'Technology Entrepreneur', 'Investor', 
    'Information Theory', 'Computer Programmer', 'NASA Astronaut', 'Test Pilot', 'Aerospace Engineer', 
    'Chemical Engineer', 'Electrical Engineer', 'Industrialist', 'Co-founder', 'Producer', 'Educator', 
    'Composer', 'Military Officer', 'Serial Killer', 'Software Engineer', 'Administrator', 
    'Mechanical Engineer', 'Manufacturer', 'Navy Officer', 'Songwriter', 'Record Producer', 
    'Civil Engineer', 'American Rapper', 'Physicist', 'Criminal', 'Cult Leader', 'Murderer', 
    'Vocalist', 'Philanthropist', 'Guitarist', 'Footballer', 'Gangster', 'Chief Executive Officer', 
    'Drug Trafficker', 'Smuggler', 'Outlaw', 'Dentist']

# Function to extract professions from the 'extract' column
def extract_professions(text):
    if pd.isna(text):
        return []
    text = text.lower()
    found_professions = set()
    for profession in professions:
        if re.search(rf'\b{profession.lower()}\b', text):
            found_professions.add(profession)
    return list(found_professions)



# Function to extract the year (assumes four consecutive digits indicate a year)
def extract_year(text):
    if pd.isna(text):
        return 'Unknown'
    match = re.search(r'\b(19|20)\d{2}\b', text)
    return match.group(0) if match else 'No Year Recorded'

# Apply the extraction functions
df['professions'] = df['extract'].apply(extract_professions)
df['year'] = df['extract'].apply(extract_year)


# Retrive column names
columns = df.columns

# Generate column definition for AG Grid
column_defs = []
for col in columns:
    column_type = 'numericColumn' if pd.api.types.is_numeric_dtype(df[col]) else \
                    'dataColumn' if pd.api.types.is_datetime64_any_dtype(df[col]) else \
                    'textColumn'
    
    column_defs.append({
        'headerName': col,
        'field': col,
        'type': column_type
    })
    

# defining the layout of the app for the Intoduction page
layout = dbc.Container([
    dbc.Row(
        dbc.Col([
            html.H5('Intoduction and Dataset Detail Page', className="text-center text-primary, mb-4"),
            html.P('This project integrates historical insights and contemporary data analysis to refine marketing strategies for the banking sector. By examining the historical evolution of key figures and events in U.S. history, alongside professional perspectives and business trends, the project identifies effective marketing strategies tailored to specific cities. The goal is to leverage this historical context and data-driven insights to optimize marketing efforts, including influencer strategies, to enhance customer engagement and drive business growth. '),
        ])
    ),
    html.H5('Dataset Information', className='text-center'),
    html.H6(''),

    dag.AgGrid(
        id='dataset_table',
        columnDefs= column_defs,
        rowData=df.to_dict('records'),
        style={'height': '600px', 'width': '100%'},
        className='ag-theme-alpine',
        resetColumnState=True,
        exportDataAsCsv=False,
        persisted_props=['selectedRows'],
        rowModelType='clientSide',
        defaultColDef={'sortable': True, 'filter': True, 'resizable': True}
    )

])
