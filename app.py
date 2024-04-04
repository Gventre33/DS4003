#Import dependencies
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State

stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app

server = app.server

# import data
df = pd.read_csv("data.csv")

# create datatable
dtable = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in sorted(df.columns)],
    sort_action="native",
    page_size=10,
    style_table={"overflowX": "auto"},
)


#---------------------------------------------------------------------------------------#
#--------------------------------------App Layout---------------------------------------#
#---------------------------------------------------------------------------------------#

# layout of the app
app.layout = html.Div([
    html.Div([
        html.H1("National Football League Team Analysis",style={'text-align': 'center'}),  # Title
        html.H2("A Visualization of Historical Data (2003-2023)",style={'text-align': 'center'}),  # Title 2
    ]),

    html.Div([],
             style={'height': '20px'}),  # Add space between description and slider/dropdown

    html.Div(dcc.RangeSlider(
        df['year'].min(),
        df['year'].max(),
        step=None,
        value=[df['year'].min()+5, df['year'].max()-7],
        marks={str(year): str(year) for year in df['year'].unique()}, # make marks based on years in df
        tooltip={"placement": "bottom", "always_visible": True},
        id='year-slider'
    ), className = 'six columns'
    ),
    html.Div(dcc.Dropdown(
        id='team-dropdown',
        options=[{'label': team, 'value': team} for team in df['team'].unique()],
        value=df['team'].unique(),  # Default of nothing selected
        multi=True  # this makes dropdown multi-select
    ), className='five columns  offset-seven',
        style={'max-height': '50px', 'overflow-y': 'auto'}
    ),
    html.Div(dcc.Dropdown(
        id='x-axis-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns[3:]],
        value=df.columns[19],  # Default of nothing selected
        # multi = True # this makes dropdown multi-select
    ), className='three columns'
    ),
    html.Div(dcc.Dropdown(
        id='y-axis-dropdown',
        options=[{'label': col, 'value': col} for col in df.columns[3:]],
        value=df.columns[25],  # Default of nothing selected
        # multi = True # this makes dropdown multi-select
    ), className='three columns'
    ),
    html.Div(dtable, className = 'six columns',style={'margin-top': '20px'}),
    html.Div(dcc.Graph(
        id='graph-with-slider'
        ), className = 'five columns' # takes up entire row
        ), 
        
], className = 'row')


#---------------------------------------------------------------------------------------#
#--------------------------------------Graph Callback-----------------------------------#
#---------------------------------------------------------------------------------------#

# define callbacks
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input('team-dropdown','value'),
     Input('x-axis-dropdown','value'),
     Input('y-axis-dropdown','value'),])
def update_figure(selected_years, selected_teams,x_axis,y_axis):
    min_year, max_year = selected_years

    filtered_df = df[(df.year >= min_year) & (df.year <= max_year)]

    # Filter by selected countries
    if selected_teams:
        filtered_df = filtered_df[filtered_df['team'].isin(selected_teams)]

    fig = px.scatter(filtered_df, x=x_axis, y=y_axis,
                     #size="pop", 
                     color="conference", hover_name="team",
                     )

    title = f"{y_axis} vs {x_axis}"
    fig.update_layout(title = title, transition_duration=500)

    # Calculate median values for x and y axes
    x_median = filtered_df[x_axis].median()
    y_median = filtered_df[y_axis].median()

    # Add lines for x and y medians
    fig.add_hline(y=y_median, line_dash="dash", line_color="red", annotation_text=f"Median {x_axis}")
    fig.add_vline(x=x_median, line_dash="dash", line_color="blue", annotation_text=f"Median {y_axis}")

    return fig

#---------------------------------------------------------------------------------------#
#--------------------------------------Data Table Callback------------------------------#
#---------------------------------------------------------------------------------------#

@app.callback(
    Output(dtable, "data"), # changes data in table
    Input('year-slider', "value"), # based on input from range_slider
)

# function that filters table based on range slider input
def update_table(slider_value): 
    if not slider_value:
        return dash.no_update
    dff = df[df.year.between(slider_value[0], slider_value[1])]
    return dff.to_dict("records")

# run app
if __name__ == '__main__':
    app.run_server(debug=True)
