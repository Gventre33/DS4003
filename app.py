{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 64,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Import dependencies\n",
    "import pandas as pd\n",
    "import seaborn as sns\n",
    "import plotly.express as px\n",
    "import matplotlib.pyplot as plt\n",
    "from dash import Dash, dcc, html, Input, Output, callback, dash_table, State\n",
    "import nfl_data_py as nfl\n",
    "import os\n",
    "import urllib.request\n",
    "from plotly.graph_objects import Layout, Scatter, Annotation, Annotations"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 59,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0       logos/NE.tif\n",
       "1       logos/NE.tif\n",
       "2       logos/NE.tif\n",
       "3       logos/NE.tif\n",
       "4       logos/NE.tif\n",
       "           ...      \n",
       "667    logos/ARI.tif\n",
       "668    logos/ARI.tif\n",
       "669    logos/ARI.tif\n",
       "670    logos/ARI.tif\n",
       "671    logos/ARI.tif\n",
       "Name: Logo Path, Length: 672, dtype: object"
      ]
     },
     "execution_count": 59,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "df_1 = pd.read_csv(\"data.csv\")\n",
    "\n",
    "# Printing the output of the last column\n",
    "df_1.iloc[:, -1]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 69,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Dash app running on http://127.0.0.1:8050/\n"
     ]
    },
    {
     "data": {
      "application/javascript": "window.open('http://127.0.0.1:8050/')",
      "text/plain": [
       "<IPython.core.display.Javascript object>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet\n",
    "\n",
    "app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app\n",
    "\n",
    "# import data\n",
    "df = pd.read_csv(\"data.csv\")\n",
    "\n",
    "# create datatable\n",
    "dtable = dash_table.DataTable(\n",
    "    columns=[{\"name\": i, \"id\": i} for i in sorted(df.columns)],\n",
    "    sort_action=\"native\",\n",
    "    page_size=10,\n",
    "    style_table={\"overflowX\": \"auto\"},\n",
    ")\n",
    "\n",
    "\n",
    "#---------------------------------------------------------------------------------------#\n",
    "#--------------------------------------App Layout---------------------------------------#\n",
    "#---------------------------------------------------------------------------------------#\n",
    "\n",
    "# layout of the app\n",
    "app.layout = html.Div([\n",
    "    html.Div([\n",
    "        html.H1(\"National Football League Team Analysis\",style={'text-align': 'center'}),  # Title\n",
    "        html.H2(\"A Visualization of Historical Data (2003-2023)\",style={'text-align': 'center'}),  # Title 2\n",
    "    ]),\n",
    "\n",
    "    html.Div([],\n",
    "             style={'height': '20px'}),  # Add space between description and slider/dropdown\n",
    "\n",
    "    html.Div(dcc.RangeSlider(\n",
    "        df['year'].min(),\n",
    "        df['year'].max(),\n",
    "        step=None,\n",
    "        value=[df['year'].min()+5, df['year'].max()-7],\n",
    "        marks={str(year): str(year) for year in df['year'].unique()}, # make marks based on years in df\n",
    "        tooltip={\"placement\": \"bottom\", \"always_visible\": True},\n",
    "        id='year-slider'\n",
    "    ), className = 'six columns'\n",
    "    ),\n",
    "    html.Div(dcc.Dropdown(\n",
    "        id='team-dropdown',\n",
    "        options=[{'label': team, 'value': team} for team in df['team'].unique()],\n",
    "        value=df['team'].unique(),  # Default of nothing selected\n",
    "        multi=True  # this makes dropdown multi-select\n",
    "    ), className='five columns  offset-seven',\n",
    "        style={'max-height': '50px', 'overflow-y': 'auto'}\n",
    "    ),\n",
    "    html.Div(dcc.Dropdown(\n",
    "        id='x-axis-dropdown',\n",
    "        options=[{'label': col, 'value': col} for col in df.columns[3:]],\n",
    "        value=df.columns[19],  # Default of nothing selected\n",
    "        # multi = True # this makes dropdown multi-select\n",
    "    ), className='three columns'\n",
    "    ),\n",
    "    html.Div(dcc.Dropdown(\n",
    "        id='y-axis-dropdown',\n",
    "        options=[{'label': col, 'value': col} for col in df.columns[3:]],\n",
    "        value=df.columns[25],  # Default of nothing selected\n",
    "        # multi = True # this makes dropdown multi-select\n",
    "    ), className='three columns'\n",
    "    ),\n",
    "    html.Div(dtable, className = 'six columns',style={'margin-top': '20px'}),\n",
    "    html.Div(dcc.Graph(\n",
    "        id='graph-with-slider'\n",
    "        ), className = 'five columns' # takes up entire row\n",
    "        ), \n",
    "        \n",
    "], className = 'row')\n",
    "\n",
    "\n",
    "#---------------------------------------------------------------------------------------#\n",
    "#--------------------------------------Graph Callback-----------------------------------#\n",
    "#---------------------------------------------------------------------------------------#\n",
    "\n",
    "# define callbacks\n",
    "@app.callback(\n",
    "    Output('graph-with-slider', 'figure'),\n",
    "    [Input('year-slider', 'value'),\n",
    "     Input('team-dropdown','value'),\n",
    "     Input('x-axis-dropdown','value'),\n",
    "     Input('y-axis-dropdown','value'),])\n",
    "def update_figure(selected_years, selected_teams,x_axis,y_axis):\n",
    "    min_year, max_year = selected_years\n",
    "\n",
    "    filtered_df = df[(df.year >= min_year) & (df.year <= max_year)]\n",
    "\n",
    "    # Filter by selected countries\n",
    "    if selected_teams:\n",
    "        filtered_df = filtered_df[filtered_df['team'].isin(selected_teams)]\n",
    "\n",
    "    fig = px.scatter(filtered_df, x=x_axis, y=y_axis,\n",
    "                     #size=\"pop\", \n",
    "                     color=\"conference\", hover_name=\"team\",\n",
    "                     )\n",
    "\n",
    "    title = f\"{y_axis} vs {x_axis}\"\n",
    "    fig.update_layout(title = title, transition_duration=500)\n",
    "\n",
    "    # Calculate median values for x and y axes\n",
    "    x_median = filtered_df[x_axis].median()\n",
    "    y_median = filtered_df[y_axis].median()\n",
    "\n",
    "    # Add lines for x and y medians\n",
    "    fig.add_hline(y=y_median, line_dash=\"dash\", line_color=\"red\", annotation_text=f\"Median {x_axis}\")\n",
    "    fig.add_vline(x=x_median, line_dash=\"dash\", line_color=\"blue\", annotation_text=f\"Median {y_axis}\")\n",
    "\n",
    "    return fig\n",
    "\n",
    "#---------------------------------------------------------------------------------------#\n",
    "#--------------------------------------Data Table Callback------------------------------#\n",
    "#---------------------------------------------------------------------------------------#\n",
    "\n",
    "@app.callback(\n",
    "    Output(dtable, \"data\"), # changes data in table\n",
    "    Input('year-slider', \"value\"), # based on input from range_slider\n",
    ")\n",
    "\n",
    "# function that filters table based on range slider input\n",
    "def update_table(slider_value): \n",
    "    if not slider_value:\n",
    "        return dash.no_update\n",
    "    dff = df[df.year.between(slider_value[0], slider_value[1])]\n",
    "    return dff.to_dict(\"records\")\n",
    "\n",
    "# run the app\n",
    "if __name__ == '__main__':\n",
    "    app.run_server(jupyter_mode = 'tab', debug=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Dash app running on http://127.0.0.1:8050/\n"
     ]
    },
    {
     "data": {
      "application/javascript": "window.open('http://127.0.0.1:8050/')",
      "text/plain": [
       "<IPython.core.display.Javascript object>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "import dash\n",
    "import pandas as pd\n",
    "from dash import Dash, dash_table, dcc, html, Input, Output, State # update to import\n",
    "import plotly.express as px\n",
    "\n",
    "#initialize app\n",
    "app = Dash(__name__)\n",
    "\n",
    "# read in data\n",
    "# import data\n",
    "df = pd.read_csv(\"data.csv\")\n",
    "\n",
    "# create range slider\n",
    "range_slider = dcc.RangeSlider(\n",
    "        df['year'].min(),\n",
    "        df['year'].max(),\n",
    "        step=None,\n",
    "        value=[df['year'].min(), df['year'].max()],\n",
    "        marks={str(year): str(year) for year in df['year'].unique()}, # make marks based on years in df\n",
    "        id='year-slider'\n",
    "    )\n",
    "\n",
    "# create datatable\n",
    "dtable = dash_table.DataTable(\n",
    "    columns=[{\"name\": i, \"id\": i} for i in sorted(df.columns)],\n",
    "    sort_action=\"native\",\n",
    "    page_size=10,\n",
    "    style_table={\"overflowX\": \"auto\"},\n",
    ")\n",
    "\n",
    "# place components in layout\n",
    "app.layout = html.Div(\n",
    "    [\n",
    "        html.H2(\"Gapminder data filtered download\", style={\"marginBottom\": 20}),\n",
    "        range_slider,\n",
    "        dtable,\n",
    "    ]\n",
    ")\n",
    "\n",
    "# write callbacks\n",
    "\n",
    "@app.callback(\n",
    "    Output(dtable, \"data\"), # changes data in table\n",
    "    Input(range_slider, \"value\"), # based on input from range_slider\n",
    ")\n",
    "\n",
    "# function that filters table based on range slider input\n",
    "def update_table(slider_value): \n",
    "    if not slider_value:\n",
    "        return dash.no_update\n",
    "    dff = df[df.year.between(slider_value[0], slider_value[1])]\n",
    "    return dff.to_dict(\"records\")\n",
    "\n",
    "# run app\n",
    "if __name__ == \"__main__\":\n",
    "    app.run_server(jupyter_mode = 'tab', debug=True)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "ds4003",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.18"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}