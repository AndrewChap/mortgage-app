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

# Helper to convert a 0-255 rgb vector to hex, should be moved to mortgagetvm module
def rgb2hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0],rgb[1],rgb[2])
# Helper to convert a space-separated string into a camelCase string, maybe should be moved to mortgagetvm module
def camel_case(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]
# Helper to perform enumerate in reverse, so that the first mortgage can be plotted on top
def reverse_enumerate(L):
   # Only works on things that have a len()
   l = len(L)
   for i, n in enumerate(L):
       yield l-i-1, n

class Call:
    def __init__(self,**kwargs):
        for key,val in kwargs.items():
            setattr(self,key,val)
        self.callback = self.call(self.name,self.prop)    
    def input_callback(self):
        return Input(self.name, self.prop)

    def __repr__(self):
        return '\nCall(' + ', '.join(["'{}':'{}'".format(key,val) for key,val in self.__dict__.items()]) + ')'

class Calls:
    def __init__(self,callDict=dict(),callList=list()):
        self.callDict = callDict
        self.callList = callList
        self.listInputs = list()
        self.listStates = list()

    def add_call(self,**kwargs):
        callIndex = len(self.callList)
        kwargs.update({'index': callIndex})
        call = Call(**kwargs)
        self.callDict[call.name] = call
        self.callList.append(call.callback)
        if call.call == State:
            callIndex = len(self.listStates)
            kwargs.update({'index': callIndex})
            self.listStates.append(call.callback)
        elif call.call == Input:
            callIndex = len(self.listInputs)+1
            kwargs.update({'index': callIndex})
            self.listInputs.append(call.callback)
        return call

    def make_kwargs(self,**kwargs):
        return kwargs
    
    def update_state_indices(self):
        for key,val in self.callDict.items():
            if val.prop == 'State':
                val.index += len(self.listInputs)
        self.callList = [self.listInputs,self.listStates]        

    def dict2list(self):
        val_list = list()
        for key,val in self.callDict.items():
            val_list.append(val)
        return val_list

    def add_button(self,name,call,text,prop='n_click',**extraKwargs):
        inputKwargs = {
            'id': name,
            prop: 0,
            'children': text,
        }
        return self.add_call(name=name,call=call,prop=prop,inputKwargs=inputKwargs)

    def add_input(self,name,call,text,type='text',prop='n_submit',**extraKwargs):
        inputKwargs = {
            'id': name,
            prop: 0,
            'value': text,
            'type': type,
        }
        inputKwargs.update(extraKwargs)
        return self.add_call(name=name,call=call,prop=prop,inputKwargs=inputKwargs)

calls = Calls()
        
# Create top bar
calculateButtonCall = calls.add_button(
    name = 'calculate',
    call = Input,
    prop = 'n_clicks',
    text = 'Calculate!',
)

calculateButton = html.Div(
    html.Button(
        **calculateButtonCall.inputKwargs
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

#max_num_mortgages = 5 # unused
num_mortgages = 3

# Create mortgages
mortgageComparison = mort.MortgageComparison()
# Set defaults
mortgageComparison.setDefaults(tvmRate       = '0.0%',
                               mortgageRate  = '4.0%',
                               downPayment   = '0.2',
                               inflationRate = '0.0%',
                               rentalRate    = '0.0%',
                               houseCost     = '$1',)

# Create mortgages
for i in range(num_mortgages):
    mortgageComparison.addMortgage(
        name = 'Mortgage {}'.format(i+1)
    )

mortgageComparison.simulateMortgages()    

dashApp = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/',
    #suppress_callback_exceptions=True,
)
dashApp.scripts.config.serve_locally = True

# Create list of divs for mortgage inputs (including global inputs)
mGroups = []

# Choose fields that user can modify
fields = ['Mortgage rate', 'Down payment', 'Origination fees']
fieldsC = [camel_case(field) for field in fields]

# Choose global options that user can modify
globs = ['TVM rate', 'House cost']
globsC = [camel_case(glob) for glob in globs]
numGlobs = len(globs)

# Create Div for global options
mGlob = [
    html.H5('Common options')
]
for j, (glob, globC) in enumerate(zip(globs,globsC)):
    inputCall = calls.add_input(
        name = globC,
        call = State,
        prop = 'value',
        text = str(getattr(mortgageComparison.mortgages[0],globC).value),
    )
    mGlob += [
        html.Label(glob, className='field-label'),    
        dcc.Input(
            **inputCall.inputKwargs
        )
    ]
# Add global options to the main group of input divs
mGroups.append(
    html.P(mGlob, className='pinput pretty-container')
)

# Add each mortgage to the main group of input divs
for i, mortgage in enumerate(mortgageComparison.mortgages):
    inputCall = calls.add_input(
        name = 'mortgage-{}-name'.format(i),
        call = State,
        prop = 'value',
        text = mortgage.name,
        className = 'mortgage-name',
        style={'color':rgb2hex(mortgage.color)}, 
    )
    mInput = [
        html.H5(
            dcc.Input(
                **inputCall.inputKwargs
            )
        )
    ]
    for j, (field, fieldC) in enumerate(zip(fields,fieldsC)):
        inputCall = calls.add_input(
            name = '{}{}'.format(fieldC,i),
            call = State,
            prop = 'value',
            text = str(getattr(mortgage,fieldC).value),
        )
        mInput += [
            html.Label(field, className='field-label'),
            dcc.Input(
                **inputCall.inputKwargs
            )
        ]
    mGroups.append(
        html.Div(mInput, className='pinput pretty-container')
    )
# Put mGroups in its own div
mGroups = html.Div(mGroups,className='input-wrapper'),

# Left panel: all the input divs (mGroups)
leftPanel = html.Div(
    html.Div(mGroups,className='panel',id='left-panel'),
    #html.Div(className='panel',id='left-panel'), # doesn't work this way yet
    className='left',
)
# Right panel: the output plot
rightPanel = html.Div(
    html.Div(    
        dcc.Graph( id = 'main-plot'),
        className='panel',
    ),
    className='right',
)

# Not sure if we need the layout to be a function yet or not
def serve_layout():
    return html.Div(children=[
        topNav,
        leftPanel,
        rightPanel,
    ])

dashApp.layout = serve_layout

# The following function is unused
@dashApp.callback(
	Output('left-panel', 'children'),
  	#[Input('div_num_dropdown', 'value')]
)
def makeMortgageDivs(num_mortgages=3):
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
    mGroups = []
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
    for i, mortgage in enumerate(mortgageComparison.mortgages):
        mInput = [
                #html.H5(mortgage.name, style={'color':rgb2hex(mortgage.color)}, className='mortgage-name')
                dcc.Input(mortgage.name, style={'color':rgb2hex(mortgage.color)}, className='mortgage-name')
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
    return html.Div(mGroups,className='input-wrapper'),

# The main plot - NEED TO GET A BETTER WAY OF MAPPING THE INPUTS
callBackList = [
    Output('main-plot', 'figure'),
    [
        calls.callDict['calculate'].input_callback(),
        #Input('calculate', 'n_clicks'),
        #calls.callDict['mortgageRate0'].input_callback(),
        #Input('mortgageRate0', 'n_submit'),
    ],
    [
        *[State('mortgage-{}-name'.format(i), 'value') for i in range(num_mortgages)],
        State('tvmRate', 'value'), 
        State('houseCost','value'),
        *[State('mortgageRate{}'.format(i), 'value') for i in range(num_mortgages)], 
        *[State('downPayment{}'.format(i), 'value') for i in range(num_mortgages)], 
        *[State('originationFees{}'.format(i), 'value') for i in range(num_mortgages)],
    ], 
]

calls.update_state_indices()
calls.callList = [Output('main-plot', 'figure')] + calls.callList
#@dashApp.callback(*callBackList)
@dashApp.callback(*calls.callList)
#def update_figure(button, *input_values):
def update_figure(*input_values):
    input_floats = [float(input_value) if type(input_value) == 'float' else input_value for input_value in input_values]
    globOptions = dict()
    for globC in globsC:
        globOptions[globC] = input_floats[calls.callDict[globC].index]
#    for j,globC in enumerate(globsC):
#        globOptions[globC] = input_values[num_mortgages + j]
    mortgageComparison.update_mortgages(options=globOptions)

    for i,mortgage in enumerate(mortgageComparison.mortgages):
        #mortgage.customName = input_values[i]
        mortgage.customName = input_values[calls.callDict['mortgage-{}-name'.format(i)].index]

        options = dict()
        for j,fieldC in enumerate(fieldsC):
            index = num_mortgages + numGlobs + i + j*num_mortgages
            #options[fieldC] = input_values[index]
            options[fieldC] = input_values[calls.callDict['{}{}'.format(fieldC,i)].index]
        mortgage.update_mortgage(options=options)    
        mortgage.simulateMortgage()
    ymin = 0.0
    ymax = 2.0
    ymax = max([mortgage.houseCost.value for mortgage in mortgageComparison.mortgages] + [np.amax(mortgage.totalAmountSpent.data) for mortgage in mortgageComparison.mortgages])
    data = [{
        'x': mortgage.timeVector.data, 
        'y': mortgage.totalAmountSpent.data,
        'name': mortgage.customName,
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


    '''
dashApp.layout = html.Div(
    [
        dcc.Dropdown(
            id='div_num_dropdown',
            options=[{'label':i, 'value':i} for i in range (5)],
            value=1
        ),
        html.Div(id='div_variable')
    ]
)
@dashApp.callback(
    Output('div_variable', 'children'),
    [Input('div_num_dropdown', 'value')]
)
def update_div(num_div):
    return [html.Div(children=f'Div #{i}') for i in range (num_div)]
'''

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
