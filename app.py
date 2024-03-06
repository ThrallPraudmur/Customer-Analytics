from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json

df = px.data.gapminder()
scatter_fig = px.scatter(df, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
           size="pop", color="continent", hover_name="country",
           log_x=True, size_max=55, range_x=[100,100000], range_y=[25,90])
scatter_fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)', font_color = 'white')

df = px.data.tips()
pie_fig = px.sunburst(df, path=['day', 'time', 'sex'], values='total_bill')
pie_fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)')


from zipfile import ZipFile

with ZipFile('data/russia_regions.zip', 'r') as myzip:
    with myzip.open('russia_regions.geojson') as f:
        geojson_data = json.load(f)

locations = {}
for feature in geojson_data['features']:
    properties = feature['properties']
    district = properties['federal_district']
    region = properties['region']
    locations[region] = district

region_data = pd.read_excel('region_data.xlsx')
region_data['Округ'] = region_data['Регион регистрации'].replace(locations)

district = {'Адыгея (Республика) (Адыгея)': 'Республика Адыгея',
 'Алтай (Республика)': 'Республика Алтай',
 'Башкортостан (Республика)': 'Республика Башкортостан',
 'Бурятия (Республика)': 'Республика Бурятия',
 'Дагестан (Республика)': 'Республика Дагестан',
 'Ингушетия (Республика)': 'Республика Ингушетия',
 'Калмыкия (Республика)': 'Республика Калмыкия',
 'Карелия (Республика)': 'Республика Карелия',
 'Коми (Республика)': 'Республика Коми',
 'Марий Эл (Республика)': 'Республика Марий Эл',
 'Мордовия (Республика)': 'Республика Мордовия',
 'Саха (Республика) (Якутия)': 'Республика Саха (Якутия)',
 'Северная Осетия-Алания (Республика)': 'Республика Северная Осетия — Алания',
 'Тыва (Республика)': 'Республика Тыва',
 'Хакасия (Республика)': 'Республика Хакасия',
 'Чувашская Республика-Чувашия': 'Чувашская Республика'}

region_data['Регион регистрации'] = region_data['Регион регистрации'].replace(district)
region_data['Округ'] = region_data['Регион регистрации'].replace(locations)

from map_figure import mapFigure, convert_crs
russia_map = mapFigure()

regions = pd.read_parquet("russia_regions.parquet")
fo_list = list(regions['federal_district'].unique())
colors = px.colors.qualitative.Pastel1

for i, r in region_data.iterrows():
    revenue_text = f"{r['2022, Выручка, RUB']:_}".replace('_', ' ')
    workers_text = f"{r['2022, Среднесписочная численность работников']:_}".replace('_', ' ')
    age_text = f"{r['Возраст компании, лет']:_}".replace('_', ' ')
    text = f"<b>{r['Регион регистрации']}</b><br>{r['Округ']} ФО<br>Средняя выручка: <b>{revenue_text}</b><br>Среднесписочная численность работников: <b>{workers_text}</b><br>Средний возраст компании: <b>{age_text} лет</b>"
    russia_map.update_traces(selector=dict(name=r['Регион регистрации']),
        text=text,
        fillcolor=colors[fo_list.index(r['Округ'])])

russia_map.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)')


data_pd = pd.read_excel('data/data_pd.xlsx')
scatter_fig = px.scatter(data_pd, x='Количество Кредитов', y='Количество Гарантий', animation_frame='Месяц', animation_group='Действие Клиента', 
                         size='Значение', color='Действие Клиента', range_x=[0,5], range_y=[-1,4], size_max=30,
                         hover_name = 'Действие Клиента',
                         # log_x=True
                        )

scatter_fig['layout'].pop('updatemenus') # optional, drop animation buttons
scatter_fig.update_traces(marker = dict(size=10, opacity=0.6), selector = dict(mode = 'markers'))
scatter_fig.update_layout(margin=dict(t=10, b=10, r=10, l=10))
scatter_fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)', font_color = 'white')

pie_data = pd.read_excel('data/pie_data.xlsx')
pie_fig = px.sunburst(pie_data, path=['Месяц', 'Продукт', 'Действие Клиента'], values='Значение', color = 'Продукт',
                      color_discrete_sequence = px.colors.sequential.Viridis, branchvalues = 'total')
pie_fig.update_traces(hovertemplate='<b>%{label} </b> <br> Сумма: %{value:.2f}', maxdepth=2, 
                      textinfo='label+percent entry', insidetextfont=dict(color='white'),
                      marker_line_color = 'white', marker_line_width = 2)

pie_fig.update_layout(uniformtext=dict(minsize=10))
pie_fig.update_layout(margin=dict(t=10, b=10, r=10, l=10))
pie_fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)', font_color = 'white')


app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
server = app.server

app.layout = html.Div([
    html.H1('Пример дашборда'),
    html.Div([dcc.Graph(figure = russia_map)])
,
    html.Div([
        dcc.Graph(figure = scatter_fig),
        dcc.Graph(figure = pie_fig)
        ], style = {'display': 'flex'})
])

if __name__ == '__main__':
    app.run(debug=True)
