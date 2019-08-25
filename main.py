import logging
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import mortgagetvm as mort
import pdb
db = pdb.set_trace
server = Flask(__name__)

mortgageComparison = mort.MortgageComparison()
mortgageComparison.setDefaults(tvmRate       = '6.0%',
                               mortgageRate  = '4.5%',
                               downPayment   = '0.2',
                               inflationRate = '0.0%',
                               rentalRate    = '0.0%',
                               houseCost     = '$1',)

num_mortgages = 2
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
    routes_pathname_prefix='/dash/'
)
dashApp.scripts.config.serve_locally = True
mGroups = []

def camel_case(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]

fields = ['Mortgage rate', 'Down payment', 'Origination fees']
fieldsC = [camel_case(field) for field in fields]

mInput = [
    html.H5('Fields'),
]
for field in fields:
    mInput += [
        html.Label(field),
    ]
mGroups.append(
    html.P(mInput, className='pinput')
)
for i, mortgage in enumerate(mortgageComparison.mortgages):
    mInput = [
        #html.H5('Mortgage {}'.format(i)),
        html.H5(mortgage.name)
    ]
    for j, (field, fieldC) in enumerate(zip(fields,fieldsC)):
        mInput += [
    #        html.Label(field),
            dcc.Input(
                id='{}{}'.format(fieldC,i),
                value=str(getattr(mortgage,fieldC).value),
                type='text',
            )
        ]
    mGroups.append(
        html.P(mInput, className='pinput')
    )
mGroups = html.Div(mGroups,className='input-wrapper'),

globalHtmls = []
globalHtmls.append(
    html.Div([
        html.Label('Home Cost')
    ])
)
mortHtmls = []
for i in range(num_mortgages):
    mortHtmls.append(
        html.Div([
            html.P([
                html.Label('Mortgage {}'.format(i)),
                html.Label('Mortgage Rate'.format(i)),
                dcc.Input(id='mir-state{}'.format(i), value='3.5', type='text'),
                html.Div(id='mir-div{}'.format(i), className='field-div'),
                html.Label('Down Payment'.format(i)),
                dcc.Input(id='mdp-state{}'.format(i), value='0.2', type='text'),
                html.Div(id='mdp-div{}'.format(i), className='field-div'),
                html.Label('Origination fees'.format(i)),
                dcc.Input(id='mof-state{}'.format(i), value='0.5', type='text'),
                html.Div(id='mof-div{}'.format(i), className='field-div'),
                #html.Div([
                #    html.Label('Mortgage Rate'.format(i)),
                #    dcc.Input(id='mir-state{}'.format(i), value='3.5', type='text'),
                #    html.Div(id='mir-div{}'.format(i), className='field-div')
                #], className='container'),
                #html.Div([
                #    html.Label('Down Payment'.format(i)),
                #    dcc.Input(id='mdp-state{}'.format(i), value='0.2', type='text'),
                #    html.Div(id='mdp-div{}'.format(i), className='field-div')
                #], className='container'),
                #html.Div([
                #    #html.Label('Origination fees'.format(i)),
                #    dcc.Input(id='mof-state{}'.format(i), value='0.5', type='text'),
                #    #html.Div(id='mof-div{}'.format(i), className='field-div')
                #], className='container'),
            ], style={'width': '150px', 'margin-right': 'auto',
           'margin-left': 'auto', 'text-align': 'center'}),
        ],style={'display': 'flex', 'flex-wrap': 'wrap'})#className='columns')
    )
dashApp.layout = html.Div(children=[
    html.H1(children='Time-value Loan & Investment Analyzer',
        style={
            'textAlign' : 'center',
        }
    ),
    *mGroups,
    #*globalHtmls,
    #*mortHtmls,
    html.Button(id='mir-button', n_clicks = 0, children='Calculate!'),
    dcc.Graph(
        id = 'main-plot',
    ),
])
#@dashApp.callback(
#    [Output('mir-div{}'.format(i), 'children') for i in range(num_mortgages)],
#    [Input('mir-button', 'n_clicks')],
#    [State('mir-state{}'.format(i), 'value') for i in range(num_mortgages)],
#)
#def update_output_div(button, *input_values):
#    input_floats = [float(input_value) for input_value in input_values]
#    return ['Rate = {:.2f}%, x = {}'.format(input_float,mortgage.netWorth.data[-1]) for input_float,mortgage in zip(input_floats,mortgages)]
@dashApp.callback(
    Output('main-plot', 'figure'),
    [Input('mir-button', 'n_clicks')],
    [State('mortgageRate{}'.format(i), 'value') for i in range(num_mortgages)] + 
    [State('downPayment{}'.format(i), 'value') for i in range(num_mortgages)] + 
    [State('originationFees{}'.format(i), 'value') for i in range(num_mortgages)], 
)
def update_figure(button, *input_values):
    input_floats = [float(input_value) for input_value in input_values]
    for i,mortgage in enumerate(mortgageComparison.mortgages):
        options = dict()
        for j,fieldC in enumerate(fieldsC):
            options[fieldC] = input_values[i+j*num_mortgages]
        mortgage.update_mortgage(options=options)    
        mortgage.simulateMortgage()
    data = [{'x': mortgage.timeVector.data, 'y': mortgage.totalAmountSpent.data} for mortgage in mortgageComparison.mortgages]
    return {
        'data': data,
        'layout': {
            #'title': 'Dash Data Visualization'
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
