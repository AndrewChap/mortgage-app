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

dashApp = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/',
    #suppress_callback_exceptions=True,
)

class InteractiveObjectsOrganizer:
    def __init__(self):
        self.dict = dict()
        self.inputList = list()
        self.stateList = list()
    def put(self,item):
        self.dict[item.name] = item
        if hasattr(item,'input'):
            self.inputList.append(item.input)
        if hasattr(item,'state'):
            self.stateList.append(item.state)
    def get(self,name):
        return self.dict[name]

interactiveDivsOrganizer = InteractiveObjectsOrganizer()

class InteractiveElement:
    def __init__(self,name,parent,operation,organizer):
        self.name = name
        self.parent = parent
        self.operation = operation
        self.input = Input(self.name,'n_clicks')
        self.organizer = organizer
        self.organizer.put(self)

class DynamicElement:
    def __init__(self,name,parent,active=False):
        self.name = name
        self.parent = parent
        self.active = active
    def make_div(self,children=None):
        if children is not None:
            self.children = children
        self.div = html.Div(children,style={})     
        self.set_visibility(active = self.active)
    def set_visibility(self,active):
        print('set visibility of {} to {}'.format(self.name,active))
        self.active = active
        display = 'block' if active else 'none'
        self.div.style.update({'display':display})
    def activate(self,*unusedArgs):    
        self.set_visibility(active=True)
    def deactivate(self,*unusedArgs):
        self.set_visibility(active=False)
        self.parent.parent.reorder_list()
        

#dashApp.scripts.config.serve_locally = True
# Choose fields that user can modify
fields = ['Mortgage rate', 'Down payment', 'Origination fees']
fieldsC = [camel_case(field) for field in fields]

# Choose global options that user can modify
globs = ['TVM rate', 'House cost']
globsC = [camel_case(glob) for glob in globs]
numGlobs = len(globs)
#------------------------------------ 
class InputField:
    def __init__(self,name,title,value,parent,index,active):
        self.name = name
        self.title = title
        self.value = value
        self.index = index
        print('making container {}-container, active = {}'.format(self.name,active))
        self.container = DynamicElement(name = '{}-container'.format(self.name),parent=self,active=active)
        print('made container {}-container, active = {}'.format(self.name,active))
        self.parent = parent
        self.make_div()
    def make_div(self):
        children = [
            html.Label(self.title,className='field-label'),
            dcc.Input(
                id = self.name,
                n_submit = 0,
                value = self.value,
                type = 'text'
            )
        ]
        self.container.make_div(children)
    def activate(self):
        self.container.set_visibility(active=True)
    def deactivate(self):
        self.container.set_visibility(active=False)


class InputBox:
    def __init__(self,parent,index,active,mortgage,fields=[]):
        #super().__init__(name=name,kinds=['Input'])
        self.name = 'div-{}'.format(index)
        self.displayName = 'Mortage {}'.format(index)
        self.index = index
        self.container = DynamicElement(name = '{}-container'.format(self.name),parent=self,active=active)
        closeContainerOperation = self.container.deactivate
        self.closeButton = InteractiveElement(
                name = '{}-closeButton'.format(self.name),
                parent=self,
                operation=closeContainerOperation,
                organizer=interactiveDivsOrganizer)
        self.fieldInputs = []
        for i,field in enumerate(fields):
            self.add_field(field,index,active=True)
        self.mortgage=mortgage
        self.make_div()
        self.parent = parent
    def add_mortgage(self,mortgage):
        self.mortgage = mortgage
    def add_field(self,field,index,active):
        print('making field {}-{}, active = {}'.format(self.name,field,active))
        self.fieldInputs.append(InputField(
            name = '{}-{}'.format(self.name,field),
            title = field,
            value = '0',
            parent = self,
            index = index,
            active = active
        ))
    def make_div(self):
        children = [
            # Button to close the div
            html.Div(
                html.Button(
                    'x',
                    id = self.closeButton.name,
                    className = 'closeButton',
                ),
                # align the close button to the right https://stackoverflow.com/a/45901157
                style={"display": "flex", "justify-content": "flex-end"}
                #style={'align':'right'}
            ),
            html.H5(
                dcc.Input(
                    value=self.displayName,
                    style={'color':rgb2hex(self.mortgage.color)}, 
                    className='mortgage-name',
                    ),
                ),
        ]
        for fieldInput in self.fieldInputs:
            children.append(fieldInput.container.div)
        formattedDiv = html.Div(children, className='pinput pretty-container')
        self.container.make_div(formattedDiv)
    def deactivate(self):
        self.container.set_visibility(active=False)

class InputBoxes:
    def __init__(self,boxesList=[],callDict=dict()):
        self.boxesList = boxesList
        self.lastNclicks = 0
        self.callDict = callDict
    def add_div(self,name,index,active,mortgage):
        inputBox = InputBox(
                parent=self,
                index=index,
                active=active,
                mortgage=mortgage,
                fields=['mortgageRate'],
                )
        self.boxesList.append(inputBox)
        #self.callDict[name] = calls
    def return_all_divs(self):
        returnList = []
        for inputBox in self.boxesList:
            returnList.append(inputBox.container.div)
        return returnList
    #def return_divs(self):
    #    returnList = []
    #    for div in self.boxesList:
    #        if div.active:
    #            returnList.append(div.div)
    #    return returnList
    def activate_next_box(self,nClicks):
        if nClicks is None:
            nClicks = 0
        if self.lastNclicks != nClicks:
            self.lastNclicks = nClicks
            for inputBox in self.boxesList:
                if not inputBox.container.active:
                    inputBox.container.activate()
                    return

    def reorder_list(self):
        activeList = []
        inactiveList = []
        for inputBox in self.boxesList:
            if inputBox.container.active:
                activeList.append(inputBox)
            else:
                inactiveList.append(inputBox)
        self.boxesList = activeList + inactiveList


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
    mortgageComparison.addMortgage(
        name = 'Mortgage {}'.format(i+1)
    )
    #inputBoxes.boxesList[-1].add_mortgage(mortgage=mortgageComparison.mortgages[-1])
    inputBoxes.add_div(
            name='div-{}'.format(i), 
            index=i, 
            active=active,
            mortgage=mortgageComparison.mortgages[-1])

mortgageComparison.simulateMortgages()    

addNewMortgageOperation = inputBoxes.activate_next_box
addNewMortgageButton = InteractiveElement(
        name = 'addNewButton',
        parent=None,
        operation=addNewMortgageOperation,
        organizer=interactiveDivsOrganizer)


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
                    id=addNewMortgageButton.name,
                ),
            ],
            className = 'top-nav',
        ),
        html.Div(id='div_variable',children=inputBoxes.return_all_divs())
    ]
)
@dashApp.callback(
    Output('div_variable', 'children'),
    interactiveDivsOrganizer.inputList,
    interactiveDivsOrganizer.stateList,
)
#def update_div(n_clicks,*n_closes):
def update_div(*inputs):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]
    triggerId = trigger['prop_id']
    triggerObj = triggerId.split('.')[0]
    triggerVal = trigger['value']
    print('ctx.triggered = {}'.format(ctx.triggered))
    print('TRIG - {}: {}'.format(triggerObj,triggerVal))
    interactiveDivsOrganizer.get(triggerObj).operation(triggerVal)
    outputDiv = html.Div(
            html.Div(
                inputBoxes.return_all_divs(),
                className='panel',id='left-panel'),
            className='left',
            )
    
    return outputDiv

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
