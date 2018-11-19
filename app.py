# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


log_file = '/home/pi/sp/temps_log'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def serve_layout():
    
    print("Page Load, refreshing data")
    df = pd.read_table(log_file)


    layout_value = html.Div(children=[
        html.H1(children='DS18B20 Sensors'),

        html.Div(children='''Monitor up to 4x temp sensors, By: Johnny Sprada'''),

        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': df['datetime'], 
                     'y': df['sensor_1'], 
                     'type': 'line', 
                     'name': 'Room'},
                    {'x': df['datetime'], 
                     'y': df['sensor_2'], 
                     'type': 'line', 
                     'name': 'Probe #1'},
                    {'x': df['datetime'], 
                     'y': df['sensor_4'], 
                     'type': 'line', 
                     'name': 'Probe #2'},
                    {'x': df['datetime'], 
                     'y': df['sensor_3'], 
                     'type': 'line', 
                     'name': 'Probe #3'},

                ],
                'layout': {
                    'title': 'Sensor Temp Over Time'
                }
            }
        )
    ])

    return layout_value

app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=True, host='192.168.1.97')