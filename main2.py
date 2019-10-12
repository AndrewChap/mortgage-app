import logging
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import mortgagetvm as mort
import pdb
import datetime
from collections import defaultdict
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
# Helper to convert a space-separated string into a camelCase string, maybe should be moved to mortgagetvm module
def from_camel_case(st):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', st)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
# Helper to perform enumerate in reverse, so that the first mortgage can be plotted on top
def reverse_enumerate(L):
   # Only works on things that have a len()
   l = len(L)
   for i, n in enumerate(L):
       yield l-i-1, n

#class Call:
#    def __init__(self,**kwargs):
#        for key,val in kwargs.items():
#            setattr(self,key,val)
#        self.callback = self.call(self.name,self.prop)    
#    def input_callback(self):
#        return Input(self.name, self.prop)
#
#    def __repr__(self):
#        return '\nCall(' + ', '.join(["'{}':'{}'".format(key,val) for key,val in self.__dict__.items()]) + ')'
#
#class Calls:
#    def __init__(self,callDict=dict(),callList=list()):
#        self.callDict = callDict
#        self.callList = callList
#        self.listInputs = list()
#        self.listStates = list()
#
#    def add_call(self,**kwargs):
#        callIndex = len(self.callList)
#        kwargs.update({'index': callIndex})
#        call = Call(**kwargs)
#        self.callDict[call.name] = call
#        self.callList.append(call.callback)
#        if call.call == State:
#            callIndex = len(self.listStates)
#            kwargs.update({'index': callIndex})
#            self.listStates.append(call.callback)
#        elif call.call == Input:
#            callIndex = len(self.listInputs)+1
#            kwargs.update({'index': callIndex})
#            self.listInputs.append(call.callback)
#        return call
#
#    def make_kwargs(self,**kwargs):
#        return kwargs
#    
#    def update_state_indices(self):
#        for key,val in self.callDict.items():
#            if val.prop == 'State':
#                val.index += len(self.listInputs)
#        self.callList = [self.listInputs,self.listStates]        
#
#    def dict2list(self):
#        val_list = list()
#        for key,val in self.callDict.items():
#            val_list.append(val)
#        return val_list
#
#    def add_button(self,name,call,text,prop='n_click',**extraKwargs):
#        inputKwargs = {
#            'id': name,
#            prop: 0,
#            'children': text,
#        }
#        return self.add_call(name=name,call=call,prop=prop,inputKwargs=inputKwargs)
#
#    def add_input(self,name,call,text,type='text',prop='n_submit',**extraKwargs):
#        inputKwargs = {
#            'id': name,
#            prop: 0,
#            'value': text,
#            'type': type,
#        }
#        inputKwargs.update(extraKwargs)
#        return self.add_call(name=name,call=call,prop=prop,inputKwargs=inputKwargs)
#
#calls = Calls()
#
#class Scene:
#    def __init__(self,mortgage,active=True):
#        self.mortgage = mortgage
#        self.active = active
#
#class Scenes:
#    def __init__(self,scenesList=list()):
#        self.scenesList = scenesList
#
#    def add_scene(self,scene):
#        self.scenesList.append(scene)
#        
## Create top bar
#calculateButtonCall = calls.add_button(
#    name = 'calculate',
#    call = Input,
#    prop = 'n_clicks',
#    text = 'Calculate!',
#)
#
#calculateButton = html.Div(
#    html.Button(
#        **calculateButtonCall.inputKwargs
#    ),
#)
#
#topNav = html.Div(
#    [
#        calculateButton,
#        html.H1(
#            "Drew & Dasha's Mortgage Analyzer",
#            className='title',
#            ),
#    ],
#    className = 'top-nav',
#)
#
##max_num_mortgages = 5 # unused
#num_mortgages = 3
#
## Create mortgages
#mortgageComparison = mort.MortgageComparison()
## Set defaults
#mortgageComparison.setDefaults(tvmRate       = '0.0%',
#                               mortgageRate  = '4.0%',
#                               downPayment   = '0.2',
#                               inflationRate = '0.0%',
#                               rentalRate    = '0.0%',
#                               houseCost     = '$1',)
#
#scenes = Scenes()
#
## Create mortgages
#for i in range(num_mortgages):
#    mortgageComparison.addMortgage(
#        name = 'Mortgage {}'.format(i+1)
#    )
#    scenes.add_scene(mortgageComparison.mortgages[-1])
#
#mortgageComparison.simulateMortgages()    
#
#dashApp = dash.Dash(
#    __name__,
#    server=server,
#    routes_pathname_prefix='/dash/',
#    #suppress_callback_exceptions=True,
#)
#dashApp.scripts.config.serve_locally = True
#
## Create list of divs for mortgage inputs (including global inputs)
#mGroups = []
#
## Choose fields that user can modify
#fields = ['Mortgage rate', 'Down payment', 'Origination fees']
#fieldsC = [camel_case(field) for field in fields]
#
## Choose global options that user can modify
#globs = ['TVM rate', 'House cost']
#globsC = [camel_case(glob) for glob in globs]
#numGlobs = len(globs)
#
## Create Div for global options
#mGlob = [
#    html.H5('Common options')
#]
#for j, (glob, globC) in enumerate(zip(globs,globsC)):
#    inputCall = calls.add_input(
#        name = globC,
#        call = State,
#        prop = 'value',
#        text = str(getattr(mortgageComparison.mortgages[0],globC).value),
#    )
#    mGlob += [
#        html.Label(glob, className='field-label'),    
#        dcc.Input(
#            **inputCall.inputKwargs
#        )
#    ]
## Add global options to the main group of input divs
#mGroups.append(
#    html.P(mGlob, className='pinput pretty-container')
#)
#
## Add each mortgage to the main group of input divs
#for i, mortgage in enumerate(mortgageComparison.mortgages):
#    inputCall = calls.add_input(
#        name = 'mortgage-{}-name'.format(i),
#        call = State,
#        prop = 'value',
#        text = mortgage.name,
#        className = 'mortgage-name',
#        style={'color':rgb2hex(mortgage.color)}, 
#    )
#    mInput = [
#        html.H5(
#            dcc.Input(
#                **inputCall.inputKwargs
#            )
#        )
#    ]
#    for j, (field, fieldC) in enumerate(zip(fields,fieldsC)):
#        inputCall = calls.add_input(
#            name = '{}{}'.format(fieldC,i),
#            call = State,
#            prop = 'value',
#            text = str(getattr(mortgage,fieldC).value),
#        )
#        mInput += [
#            html.Label(field, className='field-label'),
#            dcc.Input(
#                **inputCall.inputKwargs
#            )
#        ]
#    mGroups.append(
#        html.Div(mInput, className='pinput pretty-container')
#    )
## Put mGroups in its own div
#mGroups = html.Div(mGroups,className='input-wrapper'),
#
## Left panel: all the input divs (mGroups)
#leftPanel = html.Div(
#    html.Div(mGroups,className='panel',id='left-panel'),
#    #html.Div(className='panel',id='left-panel'), # doesn't work this way yet
#    className='left',
#)
## Right panel: the output plot
#rightPanel = html.Div(
#    html.Div(    
#        dcc.Graph( id = 'main-plot'),
#        className='panel',
#    ),
#    className='right',
#)
#
## Not sure if we need the layout to be a function yet or not
#def serve_layout():
#    return html.Div(children=[
#        topNav,
#        leftPanel,
#        rightPanel,
#    ])

#dashApp.layout = serve_layout

# The following function is unused
#@dashApp.callback(
#	Output('left-panel', 'children'),
#  	#[Input('div_num_dropdown', 'value')]
#)
#def makeMortgageDivs(num_mortgages=3):
#    mortgageComparison = mort.MortgageComparison()
#    mortgageComparison.setDefaults(tvmRate       = '0.0%',
#                                   mortgageRate  = '4.0%',
#                                   downPayment   = '0.2',
#                                   inflationRate = '0.0%',
#                                   rentalRate    = '0.0%',
#                                   houseCost     = '$1',)
#
#    num_mortgages = 3
#    for i in range(num_mortgages):
#        mortgageComparison.addMortgage(
#            name = 'Mortgage {}'.format(i+1)
#        )
#
#    mortgageComparison.simulateMortgages()    
#    mGroups = []
#    # Create column for global options
#    mGlob = [
#        html.H5('Common options')
#    ]
#    for j, (glob, globC) in enumerate(zip(globs,globsC)):
#        mGlob += [
#            html.Label(glob, className='field-label'),    
#            dcc.Input(
#                id='{}'.format(globC),
#                value=str(getattr(mortgageComparison.mortgages[0],globC).value),
#                type='text',
#            )
#        ]
#    mGroups.append(
#        html.P(mGlob, className='pinput pretty-container')
#    )
#    for i, mortgage in enumerate(mortgageComparison.mortgages):
#        mInput = [
#                #html.H5(mortgage.name, style={'color':rgb2hex(mortgage.color)}, className='mortgage-name')
#                dcc.Input(mortgage.name, style={'color':rgb2hex(mortgage.color)}, className='mortgage-name')
#        ]
#        for j, (field, fieldC) in enumerate(zip(fields,fieldsC)):
#            mInput += [
#                html.Label(field, className='field-label'),
#                dcc.Input(
#                    id='{}{}'.format(fieldC,i),
#                    value=str(getattr(mortgage,fieldC).value),
#                    type='text',
#                )
#            ]
#        mGroups.append(
#            html.Div(mInput, className='pinput pretty-container')
#        )
#    return html.Div(mGroups,className='input-wrapper'),
#
## The main plot - NEED TO GET A BETTER WAY OF MAPPING THE INPUTS
#callBackList = [
#    Output('main-plot', 'figure'),
#    [
#        calls.callDict['calculate'].input_callback(),
#        #Input('calculate', 'n_clicks'),
#        #calls.callDict['mortgageRate0'].input_callback(),
#        #Input('mortgageRate0', 'n_submit'),
#    ],
#    [
#        *[State('mortgage-{}-name'.format(i), 'value') for i in range(num_mortgages)],
#        State('tvmRate', 'value'), 
#        State('houseCost','value'),
#        *[State('mortgageRate{}'.format(i), 'value') for i in range(num_mortgages)], 
#        *[State('downPayment{}'.format(i), 'value') for i in range(num_mortgages)], 
#        *[State('originationFees{}'.format(i), 'value') for i in range(num_mortgages)],
#    ], 
#]
#
#calls.update_state_indices()
#calls.callList = [Output('main-plot', 'figure')] + calls.callList
#@dashApp.callback(*callBackList)
#@dashApp.callback(*calls.callList)
##def update_figure(button, *input_values):
#def update_figure(*input_values):
#    input_floats = [float(input_value) if type(input_value) == 'float' else input_value for input_value in input_values]
#    globOptions = dict()
#    for globC in globsC:
#        globOptions[globC] = input_floats[calls.callDict[globC].index]
##    for j,globC in enumerate(globsC):
##        globOptions[globC] = input_values[num_mortgages + j]
#    mortgageComparison.update_mortgages(options=globOptions)
#
#    for i,mortgage in enumerate(mortgageComparison.mortgages):
#        #mortgage.customName = input_values[i]
#        mortgage.customName = input_values[calls.callDict['mortgage-{}-name'.format(i)].index]
#
#        options = dict()
#        for j,fieldC in enumerate(fieldsC):
#            index = num_mortgages + numGlobs + i + j*num_mortgages
#            #options[fieldC] = input_values[index]
#            options[fieldC] = input_values[calls.callDict['{}{}'.format(fieldC,i)].index]
#        mortgage.update_mortgage(options=options)    
#        mortgage.simulateMortgage()
#    ymin = 0.0
#    ymax = 2.0
#    ymax = max([mortgage.houseCost.value for mortgage in mortgageComparison.mortgages] + [np.amax(mortgage.totalAmountSpent.data) for mortgage in mortgageComparison.mortgages])
#    data = [{
#        'x': mortgage.timeVector.data, 
#        'y': mortgage.totalAmountSpent.data,
#        'name': mortgage.customName,
#        'line': {
#            'color': rgb2hex(mortgage.color),
#            }
#        }
#        for i,mortgage in enumerate(reversed(mortgageComparison.mortgages))]
#    return {
#        'data': data,
#        'layout': {
#            'xaxis': {
#                'title': 'Time (years)',
#            },
#            'yaxis': {
#                'title': 'Amount paid towards home',
#                'range': [ymin, ymax],
#            },
#            'margin': {'t': 30, 'b': 30},
#            'legend': {'traceorder': 'reversed'},
#        }
#    }

dashApp = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/',
    #suppress_callback_exceptions=True,
)

class AllObjects:
    def __init__(self):
        self.dictionary = dict()
    def put(self,item):
        self.dictionary[item.name] = item
    def get(self,name):
        return self.dictionary[name]

allObjects = AllObjects()

class InteractiveElement:
    def __init__(self,name,parent):
        self.name = name
        self.parent = parent
        allObjects.put(self)

#dashApp.scripts.config.serve_locally = True
# Choose fields that user can modify
fields = ['Mortgage rate', 'Down payment', 'Origination fees']
fieldsC = [camel_case(field) for field in fields]

# Choose global options that user can modify
globs = ['TVM rate', 'House cost']
globsC = [camel_case(glob) for glob in globs]
numGlobs = len(globs)
#------------------------------------ 
class InputObj:
    def __init__(self,name,kinds=set()):
        self.kinds = kinds
        self.name = name
        self.inputIndex = defaultdict()
        self.inputs = defaultdict()
    def __hash__(self):
        return hash(self.name)
    def __eq__(self,other):
        return self.name == other.name

class InputObjs:
    def __init__(self):
        self.panelLists = defaultdict(list) 
        self.panelDicts = defaultdict(dict) 
    def add_obj(self,obj):
        for inputKind in obj.kinds:
            obj.inputIndex[inputKind] = len(self.panelLists[inputKind])
            self.panelLists[inputKind].append(obj.inputs[inputKind])
            self.panelDicts[inputKind][obj] = obj


class InputBox(InputObj):
    def __init__(self,name,parent,index,active=False):
        super().__init__(name=name,kinds=['Input'])
        self.name = name
        self.index = index
        #self.closeButton = InteractiveElement(name = 'close-{}'.format(self.name),parent=self)
        self.closeButton = 'close-{}'.format(self.name)
        self.inputKwargs = {
            'id': name,
            'closeButton': self.closeButton,
            #prop: 0,
            'value': self.name,
            #'type': type,
        }
        self.fields = [],
        self.inputs['Input'] = Input(self.closeButton,'n_clicks')
        self.active = active
        self.make_div()
        self.parent = parent
    def add_mortgage(self,mortgage):
        self.mortgage = mortgage
    def make_div(self):
        if self.active:
            display = 'block'
        else:
            display = 'none'
#        inputKwargs = {
#            'id': name,
#            prop: 0,
#            'value': text,
#            'type': type,
#        }
#        inputKwargs.update(extraKwargs)
#        return self.add_call(name=name,call=call,prop=prop,inputKwargs=inputKwargs)

        #inputCall = calls.add_input(
        #    name = 'mortgage-{}-name'.format(i),
        #    call = State,
        #    prop = 'value',
        #    text = mortgage.name,
        #    className = 'mortgage-name',
        #    style={'color':rgb2hex(mortgage.color)}, 
        #)
## Add each mortgage to the main group of input divs
#for i, mortgage in enumerate(mortgageComparison.mortgages):
#    inputCall = calls.add_input(
#        name = 'mortgage-{}-name'.format(i),
#        call = State,
#        prop = 'value',
#        text = mortgage.name,
#        className = 'mortgage-name',
#        style={'color':rgb2hex(mortgage.color)}, 
#    )
#    mInput = [
#        html.H5(
#            dcc.Input(
#                **inputCall.inputKwargs
#            )
#        )
#    ]
#    for j, (field, fieldC) in enumerate(zip(fields,fieldsC)):
#        inputCall = calls.add_input(
#            name = '{}{}'.format(fieldC,i),
#            call = State,
#            prop = 'value',
#            text = str(getattr(mortgage,fieldC).value),
#        )
#        mInput += [
#            html.Label(field, className='field-label'),
#            dcc.Input(
#                **inputCall.inputKwargs
#            )
#        ]
#    mGroups.append(
#        html.Div(mInput, className='pinput pretty-container')
#    )
## Put mGroups in its own div
#mGroups = html.Div(mGroups,className='input-wrapper'),
        self.div = html.Div(
            [
                html.Div(
                    self.name,
                ),
                html.Button(
                    'x',
                    id = self.closeButton,
                )
            ],
            style={'display': display},
        )
    def deactivate(self):
        self.active = False
        self.make_div()

class InputBoxes(InputObjs):
    def __init__(self,divsList=[],callDict=dict()):
        super().__init__()
        self.divsList = divsList
        self.lastNclicks = 0
        self.callDict = callDict
    def add_div(self,name,index,active=False):
        div = InputBox(name,parent=self,index=index,active=active)
        self.add_obj(div)
        self.divsList.append(div)
        #self.callDict[name] = calls
    def return_all_divs(self):
        returnList = []
        for div in self.divsList:
            returnList.append(div.div)
        return returnList
    def return_divs(self):
        returnList = []
        for div in self.divsList:
            if div.active:
                returnList.append(div.div)
        return returnList
    def activate_on_click(self,n_clicks):
        if self.lastNclicks != n_clicks:
            self.lastNclicks = n_clicks
            for div in self.divsList:
                if not div.active:
                    div.active = True
                    div.make_div()
                    return
    def find_div_by_index(self,index):
        for div in self.divsList:
            if div.index == index:
                return div
        return -1    
    def deactivate(self,closureList):
        for index,closure in enumerate(closureList):
            if closure is not None:
                self.find_div_by_index(index).deactivate()
        self.reorder_list()
    def deactivate_by_name(self,closeButton):
        index = closeButton[10]
        divToDeactivate = self.find_div_by_index(index)
        if divToDeactivate != -1:
            divToDeactivate.deactivate()
            self.reorder_list()

    def reorder_list(self):
        activeList = []
        inactiveList = []
        for div in self.divsList:
            if div.active:
                activeList.append(div)
            else:
                inactiveList.append(div)
        self.divsList = activeList + inactiveList


max_input_boxes = 6
init_input_boxes = 2
# Create mortgages
mortgageComparison = mort.MortgageComparison()
# Set defaults
mortgageComparison.setDefaults(tvmRate       = '0.0%',
                               mortgageRate  = '4.0%',
                               downPayment   = '0.2',
                               inflationRate = '0.0%',
                               rentalRate    = '0.0%',
                               houseCost     = '$1',)



inputBoxes = InputBoxes()
for i in range(max_input_boxes):
    if i < init_input_boxes:
        active = True
    else:
        active = False
    inputBoxes.add_div(name='div-{}'.format(i), index=i, active = active)
    #db()
    mortgageComparison.addMortgage(
        name = 'Mortgage {}'.format(i+1)
    )
    inputBoxes.divsList[-1].add_mortgage(mortgage=mortgageComparison.mortgages[-1])

mortgageComparison.simulateMortgages()    

dashApp.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "Drew & Dasha's Mortgage Analyzer",
                    className='title',
                ),
            ],
            className = 'title-nav',
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id='fields',
                    options = [{'label':'Rate', 'value':1},{'label':'Cost', 'value':0}],
                    #options=[{'label':i, 'value':i} for i in range (5)],
                    value=1,
                    multi=True,
                ),
                html.Button(
                    'Add New Mortgage',
                    id='add-input',
                ),
            ],
            className = 'top-nav',
        ),
        html.Div(id='div_variable',children=inputBoxes.return_all_divs())
    ]
)
@dashApp.callback(
    Output('div_variable', 'children'),
    [Input('add-input','n_clicks')] + inputBoxes.panelLists['Input'],
    inputBoxes.panelLists['State'],
)
def update_div(n_clicks,*n_closes):
#def update_div(*inputs):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]
    # Could use this trigger to update
    print('ctx.triggered = {}'.format(ctx.triggered))
    if n_clicks is None:
        n_clicks = 0
    # Deactivate any div that has been closed    
    if trigger['prop_id'].startswith('close'):
        inputBoxes.deactivate_by_name(trigger['prop_id'])
    divDeactivated = False
    for div in inputBoxes.divsList:
        if ctx.inputs[div.closeButton+'.n_clicks'] is not None:
            div.deactivate()
            divDeactivated = True
    if divDeactivated:
        inputBoxes.reorder_list()
    # "Create" new div (show new div) when button is clicked    
    if trigger['prop_id'] == 'add-input.n_clicks':
        inputBoxes.activate_on_click(n_clicks=trigger['value'])
    return inputBoxes.return_all_divs()

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
