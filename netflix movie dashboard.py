import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load data
df = pd.read_csv(r"D:\mymoviedb.csv", engine='python', on_bad_lines='skip')


# Preprocessing
df['Release_Date'] = pd.to_datetime(df['Release_Date'], errors='coerce')
df['Release_Year'] = df['Release_Date'].dt.year
df['Vote_Average'] = pd.to_numeric(df['Vote_Average'], errors='coerce')
df['Genre'] = df['Genre'].fillna("Unknown")

# Explode genres (for filtering and counting)
df['Genre_List'] = df['Genre'].str.split(', ')
df_exploded = df.explode('Genre_List')

# Dropdown filter options
genre_options = [{'label': g, 'value': g} for g in sorted(df_exploded['Genre_List'].dropna().unique())]
year_options = [{'label': int(y), 'value': int(y)} for y in sorted(df['Release_Year'].dropna().unique())]

# App setup
app = Dash(__name__)
app.title = "Netflix-style Movie Dashboard"

# Layout
app.layout = html.Div([
    html.H1("🎬 Movie & Show Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Genre:"),
        dcc.Dropdown(id='genre-filter', options=genre_options, placeholder="Filter by genre"),
    ], style={'width': '45%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Release Year:"),
        dcc.Dropdown(id='year-filter', options=year_options, placeholder="Filter by year"),
    ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),

    html.Br(), html.Br(), html.Hr(),

    dcc.Graph(id='genre-bar'),
    dcc.Graph(id='year-count'),
    dcc.Graph(id='rating-histogram'),
    dcc.Graph(id='language-distribution')
])

# Callbacks
@app.callback(
    Output('genre-bar', 'figure'),
    Output('year-count', 'figure'),
    Output('rating-histogram', 'figure'),
    Output('language-distribution', 'figure'),
    Input('genre-filter', 'value'),
    Input('year-filter', 'value')
)
def update_graphs(selected_genre, selected_year):
    filtered = df_exploded.copy()

    if selected_genre:
        filtered = filtered[filtered['Genre_List'] == selected_genre]
    if selected_year:
        filtered = filtered[filtered['Release_Year'] == selected_year]

    # Genre bar
    genre_counts = filtered['Genre_List'].value_counts().nlargest(10)
    genre_fig = px.bar(x=genre_counts.index, y=genre_counts.values, title='Top Genres', labels={'x': 'Genre', 'y': 'Count'})

    # Movies per year
    year_counts = filtered['Release_Year'].value_counts().sort_index()
    year_fig = px.bar(x=year_counts.index, y=year_counts.values, title='Movies Released per Year', labels={'x': 'Year', 'y': 'Count'})

    # Rating histogram
    rating_fig = px.histogram(filtered, x='Vote_Average', nbins=20, title='Vote Average Distribution')

    # Language pie
    lang_counts = filtered['Original_Language'].value_counts().nlargest(10)
    lang_fig = px.pie(values=lang_counts.values, names=lang_counts.index, title='Top 10 Languages')

    return genre_fig, year_fig, rating_fig, lang_fig

# Run app
if __name__ == '__main__':
    app.run(debug=True)
