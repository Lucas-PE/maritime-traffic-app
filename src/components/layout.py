from dash import html
from functions import map_functions, nav_functions

def layout(choosen_page):
    return html.Div(
        [

            # PAGE CONTENT
            html.Div(
                choosen_page, 
                id='page-content')
            
            ], className='main'
        ) 