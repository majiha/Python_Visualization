import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table
import pandas as pd
import plotly.express as px
import base64
import datetime
import io



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  ##-- es una style sheet 

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload   ##--main layout
    dcc.Upload(    
        id='upload-data',
        children=html.Div([
            'Arrastra o ',
            html.A('Carga el data set')   ##-- select files
        ]),
        style={   ##-- so it looks long and thin as it does
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded     ##-- aunq solo lo va a hacer con una
        multiple=True
    ),        ##-- two empty Divs
    html.Div(id='output-div') ,       
    html.Div(id='output-datatable'),  
])


def parse_contents(contents, filename, date):  
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(                            ##-- si es un csv lo convertimos a pandas dataframe
                io.StringIO(decoded.decode('utf-8')))

    except Exception as e:
        print(e)
        return html.Div([
            'Error'
        ])

    return html.Div([          ##--  ahora que hemos creado los panda dataframes ya podemos empezar a return cosas
        html.H5(filename, style={'textAlign': 'center'}),   ##-- header con el nombre del dataframe

        html.P("Escoge el tipo de gráfico: ", style={'textAlign': 'center'}),
        dcc.RadioItems(id="graph-selected",
                        options=[ {'label':'Líneas', 'value':'line'},
                                  {'label':'Barras', 'value':'bar'},
                                  {'label':'Puntos', 'value': 'scatter'},
                                  {'label':'Histograma', 'value': 'hist'}],
                        style={'textAlign': 'center'},
                        value = 'bar'
        ),
        html.P("Seleccione el eje X"),  ##-- parrafo con esta frase
        dcc.Dropdown(id='xaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),   ##-- las opciones a elegir son las columnas del dataframe importado
        html.P("Seleccione el eje Y"),
        dcc.Dropdown(id='yaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns]),  
        html.Button(id="submit-button", children="Crear Gráfico"),   ##-- boton para crear el grafico
        html.Hr(),

        dash_table.DataTable(       ##-- creamos una tabla
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15          ##-- 15 filas por pagina
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),    ##-- guardamos la tabla de datos

        html.Hr(), 

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),   
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None: 
        children = [
            parse_contents(c, n, d) for c, n, d in  ##-- esta invocando la funcion anteriormente creada
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-div', 'children'),   
              Input('submit-button','n_clicks'),   ##-- hace falsa clickar el botón para ejecutar el callback
              State('graph-selected', 'value'),
              State('stored-data','data'),      ##-- los cambios hechos en State no se verán reflejados hasta que no clickemos en el botón
              State('xaxis-data','value'),
              State('yaxis-data', 'value'))
def make_graphs(n, graph_chosen, data, x_data, y_data):
    if n is None:    ##-- n es n_clicks osea que si no se presiona el boton que no se realicen cambios
        return dash.no_update
    elif graph_chosen == 'line':
        line_fig = px.line(data, x=x_data, y=y_data)
        return dcc.Graph(figure=line_fig) 
    elif graph_chosen == 'bar':          
        bar_fig = px.bar(data, x=x_data, y=y_data)   
        return dcc.Graph(figure=bar_fig)    
    elif graph_chosen == 'scatter':
        scatter_fig = px.scatter(data, x=x_data, y=y_data)
        return dcc.Graph(figure=scatter_fig) 
    elif graph_chosen == 'hist':
        hist_fig = px.histogram(data, x=x_data, y=y_data)
        return dcc.Graph(figure=hist_fig) 



if __name__ == '__main__':
    app.run_server(debug=True)