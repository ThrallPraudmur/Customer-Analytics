from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
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

region_data = pd.read_excel('data/region_data.xlsx')
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
 'Чувашская Республика-Чувашия': 'Чувашская Республика',
#  'Ямало-Ненецкий автономный округ': 'Тюменская область',
#  'Ненецкий автономный округ': 'Архангельская область',
#  'Ханты-Мансийский автономный округ — Югра': 'Тюменская область'
            }
additional_data = pd.DataFrame()
for region in ['Ямало-Ненецкий автономный округ', 'Ханты-Мансийский автономный округ — Югра']:
    tyumen_data = region_data.loc[region_data['Регион регистрации'] == 'Тюменская область'].copy()
    tyumen_data['Регион регистрации'] = region
    additional_data = pd.concat([additional_data, tyumen_data])

archangel_data = region_data.loc[region_data['Регион регистрации'] == 'Архангельская область'].copy()
archangel_data['Регион регистрации'] = 'Ненецкий автономный округ'

region_data = pd.concat([region_data, additional_data], ignore_index = True)
region_data = pd.concat([region_data, archangel_data], ignore_index = True)
region_data['Регион регистрации'] = region_data['Регион регистрации'].replace(district)
region_data['Округ'] = region_data['Регион регистрации'].replace(locations)

from map_figure import mapFigure, convert_crs
russia_towns = mapFigure()

fo_list = list(region_data['Округ'].unique())
colors = px.colors.qualitative.Pastel1

for i, r in region_data.iterrows():
    revenue_text = f"{r['2022, Выручка, RUB']:_}".replace('_', ' ')
    workers_text = f"{r['2022, Среднесписочная численность работников']:_}".replace('_', ' ')
    age_text = f"{r['Возраст компании, лет']:_}".replace('_', ' ')
    text = f"<b>{r['Регион регистрации']}</b><br>{r['Округ']} ФО<br>Выручка: <b>{revenue_text}</b><br>Численность работников: <b>{workers_text}</b><br>Возраст: <b>{age_text} лет</b>"
    russia_towns.update_traces(selector=dict(name=r['Регион регистрации']),
        text=text,
        fillcolor=colors[fo_list.index(r['Округ'])])

russia_towns.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)')
russia_towns.update_layout(margin=dict(t=10, b=10, r=10, l=10))

df = pd.read_parquet("data/russia_cities_population.parquet")
# координаты в требуемой для карты системе отсчёта
df['x'], df['y'] = convert_crs(df.lon, df.lat)

df = df.sort_values(['population'], ascending = False).head(15)

# палитра цветов для точек
cities_palette = {fd: px.colors.qualitative.Dark2_r[i] for i, fd in enumerate(df.federal_district.unique())}

# добавление точек на фигуру
russia_towns.add_trace(go.Scatter(
    x=df.x, y=df.y, name='города',
    text="<b>"+df.city+"</b><br>Население <b>"+df.population.astype('str')+"</b>",
    hoverinfo="text", showlegend=False, mode='markers',
    marker_size=df.population/1e4, marker_sizemode='area', marker_sizemin=3,
    marker_color=df.federal_district.map(cities_palette)
))

with open('data/ru.json', 'r') as f:
    counties = json.load(f)

data_map = pd.read_excel('data/data_map.xlsx')
russia_map = px.choropleth_mapbox(data_map[data_map['REVENUE_BACKET'] == '200-500'],
                               geojson = counties, locations = 'ID', featureidkey = 'id', color = 'ACC_FREE_SAL', mapbox_style = 'carto-positron',
                               zoom = 4, center = {'lat': 55.45, 'lon': 37.36}, animation_frame = 'MONTH_NUMBER', color_continuous_scale = 'RdYlGn',
                               opacity = 0.7, template = 'plotly_dark',
                               hover_data = {'ID': False, 'Регион': True, 'ACC_FREE_SAL': True, 'MONTH_NUMBER': False}
                                  )

russia_map.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)', coloraxis_showscale = False)
russia_map.update_layout(margin=dict(t=10, b=10, r=10, l=10))

centro_data = pd.read_excel('data/centro_data.xlsx')
centro_data['Месяц'] = centro_data['Месяц'].apply(lambda x: x.strftime('%Y-%m-%d'))

dep_map = px.choropleth_mapbox(dep_data, geojson = counties, locations = 'ID', featureidkey = 'id', color = 'РУБЛИ', mapbox_style = 'carto-positron',
                               zoom = 4, center = {'lat': 55.45, 'lon': 37.36}, animation_frame = 'Месяц', color_continuous_scale = 'RdYlGn',
                               opacity = 0.7, template = 'plotly_dark',
                               hover_data = {'ID': False, 'Регион': True, 'РУБЛИ': True, 'Месяц': False}, title = 'Депозиты юр. лиц, млн. руб.'
                     )

dep_map.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)', coloraxis_showscale = False)
dep_map.update_layout(margin=dict(t=30, b=10, r=10, l=10))

funds_map = px.choropleth_mapbox(funds_data, geojson = counties, locations = 'ID', featureidkey = 'id', color = 'РУБЛИ', mapbox_style = 'carto-positron',
                               zoom = 4, center = {'lat': 55.45, 'lon': 37.36}, animation_frame = 'Месяц', color_continuous_scale = 'RdYlGn',
                               opacity = 0.7, template = 'plotly_dark',
                               hover_data = {'ID': False, 'Регион': True, 'РУБЛИ': True, 'Месяц': False}, title = 'Средства на счетах организаций, млн. руб.'
                     )

funds_map.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)', coloraxis_showscale = False)
# funds_map.update_layout(title=dict(text = 'Средства на счетах орг., млн.руб.', font = dict(size = 20)))
funds_map.update_layout(margin=dict(t=30, b=10, r=10, l=10))

backet_selector = dcc.Dropdown(
    data_map['REVENUE_BACKET'].unique().tolist(), '200-500', id = 'backet-selector'
)

parametr_selector = dcc.Dropdown(
    ['ACC_FREE_SAL', 'BG_AMOUNT_ACTIVE', 'ACC_TRN_MYSELF_DB', 'ACC_TRN_EXT_DB', 'LIZ_CNT_ACTIVE', 'COMIS_AMOUNT'], 'ACC_FREE_SAL', id = 'parametr-selector'
)

currency_selector = dcc.Dropdown(
    ['РУБЛИ', 'ВАЛЮТА'], 'РУБЛИ', id = 'currency-selector'
)

product_selector = dcc.Dropdown(
    ['СРЕДСТВА НА СЧЕТАХ', 'ДЕПОЗИТЫ'], 'СРЕДСТВА НА СЧЕТАХ', id = 'product-selector'
)

funds_data = centro_data[['Месяц', 'Средства на счетах орг., млн.руб._x', 'Средства на счетах орг., млн.руб._y', 'Регион', 'ID']]
funds_data.rename(columns = {
    'Средства на счетах орг., млн.руб._x': 'РУБЛИ',
    'Средства на счетах орг., млн.руб._y': 'ВАЛЮТА'
}, inplace = True)

dep_data = centro_data[['Месяц',  'Депозиты юр.лиц, млн.руб._x', 'Депозиты юр.лиц, млн.руб._y', 'Регион', 'ID']]
dep_data.rename(columns = {
    'Депозиты юр.лиц, млн.руб._x': 'РУБЛИ',
    'Депозиты юр.лиц, млн.руб._y': 'ВАЛЮТА'
}, inplace = True)

nash_content = dbc.Row([
        dbc.Col([
            dcc.Graph(figure = russia_map, id = 'russia-map'),
        ], width = {'size': 8}),
        dbc.Col([
            html.Div('BACKET', style = {'color': 'white'}),
            html.Div(backet_selector),
            html.Div('В разрезе чего смотрим', style = {'color': 'white'}),
            html.Div(parametr_selector)
        ], width = {'size': 2}),
    ], style = {'margin-bottom': 40, 'margin-top': 20})

banki_content = dbc.Row([
        dbc.Col([
            dcc.Graph(figure = funds_map, id = 'banki-map'),
        ], width = {'size': 8}),
        dbc.Col([
            html.Div('ПРОДУКТ', style = {'color': 'white'}),
            html.Div(product_selector),
            html.Div('ВАЛЮТА', style = {'color': 'white'}),
            html.Div(currency_selector)
        ], width = {'size': 2}),
    ], style = {'margin-bottom': 40, 'margin-top': 20})

geo_content = [
    # Карта России
    dbc.Row([
        dbc.Col([
            html.H4('Портрет клиента по России'),
            dcc.Graph(figure = russia_towns, id = 'russia-towns')
        ]),
        dbc.Col([
            # html.Div(id = 'click-data-output')
        ], )
    ], style = { 'margin-bottom': 40, 'margin-top': 20}),

    dbc.Tabs([
        dbc.Tab(banki_content, 
                label = 'Данные Центробанка'),
        dbc.Tab(nash_content, 
                label = 'Наши Клиенты')
    ]),
]

# Пирог
pie_data = pd.read_excel('data/pie_data.xlsx')
pie_fig = px.sunburst(pie_data, path=['Месяц', 'Продукт', 'Действие Клиента'], values='Значение', color = 'Продукт',
                      color_discrete_sequence = px.colors.sequential.Viridis, branchvalues = 'total')
pie_fig.update_traces(hovertemplate='<b>%{label} </b> <br> Сумма: %{value:.2f}', maxdepth=2, 
                      textinfo='label+percent entry', insidetextfont=dict(color='white'),
                      marker_line_color = 'white', marker_line_width = 2)

pie_fig.update_layout(uniformtext=dict(minsize=10))
pie_fig.update_layout(margin=dict(t=10, b=10, r=10, l=10))
pie_fig.update_layout(paper_bgcolor = 'rgba(0,0,0,0)', font_color = 'white')

# Тепловая карта
merged_df = pd.read_excel('data/merged_df.xlsx')
heatmap = px.imshow(merged_df.pivot_table(index = 'Продукт', columns = 'Дата комментария', values = 'label'), 
                color_continuous_midpoint = 0,
                color_continuous_scale = ['red', 'green'], 
                template = 'plotly_dark',
                # origin = 'lower'
               )
heatmap.update_layout(margin=dict(t=10, b=10, r=10, l=10))
heatmap.update_layout(paper_bgcolor = 'rgba(0,0,0,0)', font_color = 'white', plot_bgcolor = 'rgba(0,0,0,0)', coloraxis_showscale = False)

# Комментатор - Навигатор
category_order = ['Депозит', 'Кредит', 'РКО', 'Лизинг', 
                  'Cтрахование', 'Факторинг', 'Эквайринг',
                  'ЗПП', 'Страхование', 'ВЭД', 'Продукты'
                 ]

data_copy = merged_df.copy()
data_copy['label'].replace({-500: 500}, inplace = True)
category_order = ['Депозит', 'Кредит', 'РКО', 'Лизинг', 
                  # 'Факторинг', 'Эквайринг',
                  'ЗПП', 'Страхование', 
                  # 'ВЭД', 
                  'Продукты', 'Финансирование'
                 ]

fig = px.bar_polar(data_copy.fillna(0), 
                   r = 'label', # Values are used to position marks along the radial axis in polar coordinates
                   theta = 'Продукт', #Values are used to position marks along the angular axis in polar coordinates
                   category_orders = {'Продукт': category_order},
                   color = 'Отношение', 
                   animation_group = 'Отношение', animation_frame = 'Дата комментария',
                   template = 'plotly_dark',
                   hover_data = {'Дата комментария': False, 'Отношение': False, 'Продукт': False, 'label': False},
                   hover_name = 'Комментарий',
                   # color_discrete_sequence= ['red', 'green'] # В том порядке, что встречается в данных
                   color_discrete_map = {'Интерес': 'green', 'Не актуально': 'red'}
                  )

fig['layout'].pop('updatemenus') # optional, drop animation buttons
fig.update_layout(showlegend = False,
                  polar = dict(radialaxis = dict(showticklabels = False)),
                  paper_bgcolor = 'rgba(0,0,0,0)', font_color = 'white')
                  
app = Dash(__name__, external_stylesheets = [dbc.themes.FLATLY])
server = app.server

# LAYOUT
app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Img(src = app.get_asset_url('images/logo.png'), style = {'width': '150px', 'margin-left': '80px', 'background-color': 'transparent'})
        ], width = {'size': 2}),
        dbc.Col([
            html.H2('Пример интерактивного дашборда'),
        ], width = {'size': 7, 'offset': 1}),
    ], className = 'app-header'),
    html.Div([
    dbc.Tabs([
        dbc.Tab(geo_content, label = 'Геоаналитика (?)'),
        dbc.Tab(html.Div([
        dcc.Graph(figure = scatter_fig),
        dcc.Graph(figure = pie_fig)
        ], style = {'display': 'flex'}), label = 'Анализ активности'),
        dbc.Tab(html.Div([
        dcc.Graph(figure = heatmap),
        dcc.Graph(figure = fig)
        ], style = {'display': 'flex'}), label = 'Анализ комментариев'),
    ]),
    html.Div(style = {'height': '200px'}),
    ], className = 'app-body')], style = {'background-color': '#121320'})


@app.callback(
    Output(component_id = 'russia-map', component_property = 'figure'),
    Output(component_id = 'banki-map', component_property = 'figure'),
    [Input(component_id = 'backet-selector', component_property = 'value'),
     Input(component_id = 'parametr-selector', component_property = 'value'),
     Input(component_id = 'product-selector', component_property = 'value'),
     Input(component_id = 'currency-selector', component_property = 'value')]
)
def update_maps(backet_value, parametr_value, product_value, currency_value):
    fig1 = px.choropleth_mapbox(data_map[data_map['REVENUE_BACKET'] == backet_value],
                               geojson = counties, locations = 'ID', featureidkey = 'id', color = parametr_value, mapbox_style = 'carto-positron',
                               zoom = 4, center = {'lat': 55.45, 'lon': 37.36}, animation_frame = 'MONTH_NUMBER', color_continuous_scale = 'RdYlGn',
                               opacity = 0.7, template = 'plotly_dark',
                               hover_data = {'ID': False, 'Регион': True, parametr_value: True, 'MONTH_NUMBER': False}
                                  )
    fig1.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)', coloraxis_showscale = False)
    fig1.update_layout(margin=dict(t=30, b=10, r=10, l=10))

    if product_value == 'СРЕДСТВА НА СЧЕТАХ':
        fig2 = px.choropleth_mapbox(funds_data, geojson = counties, locations = 'ID', featureidkey = 'id', color = currency_value, mapbox_style = 'carto-positron',
                               zoom = 4, center = {'lat': 55.45, 'lon': 37.36}, animation_frame = 'Месяц', color_continuous_scale = 'RdYlGn',
                               opacity = 0.7, template = 'plotly_dark',
                               hover_data = {'ID': False, 'Регион': True, currency_value: True, 'Месяц': False}, title = 'Средства на счетах организаций, млн. руб.'
                     )
        fig2.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)', coloraxis_showscale = False)
        fig2.update_layout(margin=dict(t=30, b=10, r=10, l=10))

    if product_value == 'ДЕПОЗИТЫ':
        fig2 = px.choropleth_mapbox(dep_data, geojson = counties, locations = 'ID', featureidkey = 'id', color = currency_value, mapbox_style = 'carto-positron',
                               zoom = 4, center = {'lat': 55.45, 'lon': 37.36}, animation_frame = 'Месяц', color_continuous_scale = 'RdYlGn',
                               opacity = 0.7, template = 'plotly_dark',
                               hover_data = {'ID': False, 'Регион': True, currency_value: True, 'Месяц': False}, title = 'Депозиты юр.лиц, млн. руб.'
                     )
        fig2.update_layout(plot_bgcolor = 'rgba(0,0,0,0)', paper_bgcolor = 'rgba(0,0,0,0)', coloraxis_showscale = False)
        fig2.update_layout(margin=dict(t=30, b=10, r=10, l=10))    

    return fig1, fig2

if __name__ == '__main__':
    app.run(debug=True)