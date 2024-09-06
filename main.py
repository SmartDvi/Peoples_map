import dash
from dash import dcc, Output, callback, State, html
import dash_bootstrap_components as dbc
import pandas as pd



# Initialize the Dash app
app = dash.Dash(__name__, use_pages= True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# define the layout of the app
app.layout =dbc.Container([
        html.H1('USA Views Analysis Dashboard', className='page-header'),

        # styling the navigation link
        dbc.Nav(
            [
                dbc.NavItem(
                    dbc.NavLink(f'{page['name']}', href=page['relative_path'], className='dash-link', active='exact' )
                ) for page in dash.page_registry.values()
            ],
            className = 'nav-links',
            pills=True,
        ),
        # customizing the page container with styling
        html.Div(dash.page_container, className='page-container'),

        # developing the footer
        dbc.Row(
            [
                dbc.Col(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink('Data Source', href='https://github.com/plotly/Figure-Friday/tree/main/2024/week-35', target="_blank")),
                            dbc.NavItem(dbc.NavLink('Source Code', href='https://github.com/SmartDvi/Peoples_map.git', target="_blank")),
                           

                        ],
                        className='footer-links',
                        pills=True,
                        


                    ),
                    width='auto',
                    className='text-center mt-4'
                )
            ],
            justify='center'
        )
    ],
    fluid=True

)
if __name__ == "__main__":
    app.run(debug=True, port=6530)




    