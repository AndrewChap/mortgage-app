import logging
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import mortgagetvm as mort
import pdb
import datetime
db = pdb.set_trace
import numpy as np
server = Flask(__name__)


def rgb2hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0],rgb[1],rgb[2])
def reverse_enumerate(L):
   # Only works on things that have a len()
   l = len(L)
   for i, n in enumerate(L):
       yield l-i-1, n

mortgageComparison = mort.MortgageComparison()
mortgageComparison.setDefaults(tvmRate       = '0.0%',
                               mortgageRate  = '4.0%',
                               downPayment   = '0.2',
                               inflationRate = '0.0%',
                               rentalRate    = '0.0%',
                               houseCost     = '$1',)

num_mortgages = 3
for i in range(num_mortgages):
    mortgageComparison.addMortgage(
        name = 'Mortgage {}'.format(i+1)
    )

mortgageComparison.simulateMortgages()    
mortgages = [mort.Mortgage() for _ in range(num_mortgages)]
for mortgage in mortgages:
   mortgage.simulateMortgage()

dashApp = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/',
    show_undo_redo=True,
    suppress_callback_exceptions=True,
)
dashApp.scripts.config.serve_locally = True
mGroups = []

def camel_case(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]

fields = ['Mortgage rate', 'Down payment', 'Origination fees']
fieldsC = [camel_case(field) for field in fields]

globs = ['TVM rate', 'House cost']
globsC = [camel_case(glob) for glob in globs]
numGlobs = len(globs)

# Create column for global options
mGlob = [
    html.H5('Common options')
]
for j, (glob, globC) in enumerate(zip(globs,globsC)):
    mGlob += [
        html.Label(glob, className='field-label'),    
        dcc.Input(
            id='{}'.format(globC),
            value=str(getattr(mortgageComparison.mortgages[0],globC).value),
            type='text',
        )
    ]
mGroups.append(
    html.P(mGlob, className='pinput pretty-container')
)

# Create column for labels for mortgage-specific options:
#mLabels = [
#    html.H5('Fields'),
#]
#for field in fields:
#    mLabels += [
#        html.Label(field),
#    ]
#mGroups.append(
##    html.P(mLabels, className='pinput')
#)
calculateButton = html.Div(
    html.Button(
        id='calculate',
        n_clicks = 0,
        children='Calculate!'
    ),
)

topNav = html.Div(
    [
        calculateButton,
        html.H1(
            "Drew & Dasha's Mortgage Analyzer",
            className='title',
            ),
    ],
    className = 'top-nav',
)


mRows = []
firstRow = []
firstRow.append(
    html.Div(
        html.H5('Hello!'),
        className='div-table-col',
    )
)
for i, mortgage in enumerate(mortgageComparison.mortgages):
    firstRow.append(
        html.Div(
            html.H5(mortgage.name),
            className = 'div-table-col',
        )
    )
firstRow = html.Div(firstRow,className='div-table-row')

for i, mortgage in enumerate(mortgageComparison.mortgages):
    mInput = [
            html.H5(mortgage.name, style={'color':rgb2hex(mortgage.color)}, className='mortgage-name')
    ]
    for j, (field, fieldC) in enumerate(zip(fields,fieldsC)):
        mInput += [
            html.Label(field, className='field-label'),
            dcc.Input(
                id='{}{}'.format(fieldC,i),
                value=str(getattr(mortgage,fieldC).value),
                type='text',
            )
        ]
    mGroups.append(
        html.Div(mInput, className='pinput pretty-container')
    )
#mGroups.append(
#    html.Div(
#        html.Button(
#            id='calculate',
#            n_clicks = 0,
#            children='Calculate!'
#        ),
#        className = 'pretty-container',
#    )    
#)
mGroups = html.Div(mGroups,className='input-wrapper'),

globalHtmls = []
globalHtmls.append(
    html.Div([
        html.Label('Home Cost')
    ])
)
leftPanel = html.Div(
    html.Div(mGroups,className='panel'),
    className='left',
)
rightPanel = html.Div(
    html.Div(    
        dcc.Graph( id = 'main-plot'),
        className='panel',
    ),
    className='right',
)

def serve_layout():
    return html.Div(children=[
        topNav,
        leftPanel,
        rightPanel,
    ])

#def serve_layout():
#    return html.H5('The time is: ' + str(datetime.datetime.now()))

dashApp.layout = serve_layout


@dashApp.callback(
    Output('main-plot', 'figure'),
    [Input('calculate', 'n_clicks')],
    [State('tvmRate', 'value'), State('houseCost','value')] + 
    [State('mortgageRate{}'.format(i), 'value') for i in range(num_mortgages)] + 
    [State('downPayment{}'.format(i), 'value') for i in range(num_mortgages)] + 
    [State('originationFees{}'.format(i), 'value') for i in range(num_mortgages)], 
)
def update_figure(button, *input_values):
    input_floats = [float(input_value) for input_value in input_values]
    globOptions = dict()
    for j,globC in enumerate(globsC):
        globOptions[globC] = input_values[j]
    mortgageComparison.update_mortgages(options=globOptions)


    for i,mortgage in enumerate(mortgageComparison.mortgages):
        options = dict()
        for j,fieldC in enumerate(fieldsC):
            index = numGlobs + i + j*num_mortgages
            options[fieldC] = input_values[index]
        mortgage.update_mortgage(options=options)    
        mortgage.simulateMortgage()
    ymin = 0.0
    ymax = 2.0
    ymax = max([mortgage.houseCost.value for mortgage in mortgageComparison.mortgages] + [np.amax(mortgage.totalAmountSpent.data) for mortgage in mortgageComparison.mortgages])
    data = [{
        'x': mortgage.timeVector.data, 
        'y': mortgage.totalAmountSpent.data,
        'name': mortgage.name,
        'line': {
            'color': rgb2hex(mortgage.color),
            }
        }
        for i,mortgage in enumerate(reversed(mortgageComparison.mortgages))]
    return {
        'data': data,
        'layout': {
            'xaxis': {
                'title': 'Time (years)',
            },
            'yaxis': {
                'title': 'Amount paid towards home',
                'range': [ymin, ymax],
            },
            'margin': {'t': 30, 'b': 30},
            'legend': {'traceorder': 'reversed'},
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
