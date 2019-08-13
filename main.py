####################################################################### Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_flex_quickstart]
import logging

from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import mortgagetvm as mort

server = Flask(__name__)

num_mortgages = 2
mortgages = [mort.Mortgage() for _ in range(num_mortgages)]
for mortgage in mortgages:
   mortgage.simulateMortgage()


dashApp = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/'
)
dashApp.scripts.config.serve_locally = True


dashApp.layout = html.Div(children=[
    html.H1(children='Time-value Loan & Investment Analyzer',
	    style={
                'textAlign' : 'center',
		}
),
    dcc.Graph(
        id = 'main-plot',
    ),
    html.Label('Text Input'),
    dcc.Input(id='mir-state', value='3.5', type='text'),
    html.Button(id='mir-button', n_clicks = 0, children='Calculate!'),
    html.Div(id='mir-div')
])

@dashApp.callback(
    Output('mir-div', 'children'),
    [Input('mir-button', 'n_clicks')],
    [State('mir-state', 'value')],
)
def update_output_div(button, input_value):
    input_float = float(input_value)
    return 'Rate = {:.2f}%, x[0] = {}'.format(input_float,mortgages[0].netWorth.data[-1])

@dashApp.callback(
    Output('main-plot', 'figure'),
    [Input('mir-button', 'n_clicks')],
    [State('mir-state', 'value')],
)
def update_figure(button, input_value):
    input_float = float(input_value)
    for i in range(num_mortgages):
        mortgages[i] = mort.Mortgage(mortgageRate=input_value)
        mortgages[i].simulateMortgage()
    data = [{'x': mortgage.timeVector.data, 'y': mortgage.netWorth.data} for mortgage in mortgages]
    return {
        'data': data,
        'layout': {
            'title': 'Dash Data Visualization'
        }
    }


@server.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    #dashApp.run_server(host='127.0.0.1', port=8080, debug=True)
    dashApp.run_server(debug=True)
    #server.run(host='127.0.0.1', port=8080, debug=True)


# [END gae_flex_quickstart]
