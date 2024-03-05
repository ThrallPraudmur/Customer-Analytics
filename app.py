from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

df = px.data.gapminder()
scatter_fig = px.scatter(df, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
           size="pop", color="continent", hover_name="country",
           log_x=True, size_max=55, range_x=[100,100000], range_y=[25,90])
scatter_fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)', font_color = 'white')

df = px.data.tips()
pie_fig = px.sunburst(df, path=['day', 'time', 'sex'], values='total_bill')
pie_fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)')

app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
server = app.server

app.layout = html.Div(

    html.Div([
        dcc.Graph(figure = scatter_fig),
        dcc.Graph(figure = pie_fig)
        ], style = {'display': 'flex'})
)


if __name__ == '__main__':
    app.run(debug=True)
