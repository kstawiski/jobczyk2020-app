import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
from pysurvival.models.semi_parametric import NonLinearCoxPHModel
import pandas as pd
from dash.dependencies import Input, Output, State
from pysurvival.utils import load_model
from toolbox import *
from dash_table import DataTable

#read torch models

pfsMod = load_model('modelData/final_pfs.zip')
rfsMod = load_model('modelData/final_rfs.zip')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.GRID]



app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

#app.css.config.serve_locally = True
#app.scripts.config.serve_locally = True


app.layout = html.P(id = 'page_content', className = 'app_body', children = [

    dbc.Row(),

    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(id = 'inputBar', children = [
                        html.H4(children = '1. Input patient data.'),
                        html.P("Please enter the values of following parameters: ", className = 'normalny'),

                        #gender
                        html.Label('Gender [M/F] '),
                        dcc.Dropdown(
                            id = 'gender',
                            options = [
                                {'label' : 'Female', 'value' : 1},
                                {'label' : 'Male', 'value' : 0}
                            ],
                            value = 1
                        ),

                        #age
                        html.Label('Age [years]'),
                        dcc.Input(id = 'age', type = 'number', value = 74),

                        #T
                        html.Label('T [numerical]'),
                        dcc.Dropdown(
                            id = 't',
                            options = [
                                {'label' : 'Ta', 'value' : 0},
                                {'label' : 'T1', 'value' : 1}
                            ],
                            value = 0
                        ),

                        #Grading
                        html.Label('Grade'),
                        dcc.Dropdown(
                            id = 'grade',
                            options = [{'label' : i, 'value' : i} for i in [1, 2, 3]],
                            value = 1
                        ),

                        #nTumors
                        html.Label('Number of tumors'),
                        dcc.Dropdown(
                            id = 'tumors',
                            options = [
                                {'label' : 'Single tumor', 'value' : 0},
                                {'label' : 'Multiple tumors', 'value' : 1}
                            ],
                            value = 0
                        ),

                        #diameter
                        html.Label('Diameter [cm]'),
                        dcc.Dropdown(
                            id = 'diam',
                            options = [
                                {'label' : 'Smaller than 3 cm', 'value' : 0},
                                {'label' : '3 cm or bigger', 'value' : 1}
                            ],
                            value = 1
                        ),

                        #concurrent Cis
                        html.Label('Is concurrent CIS present?'),
                        dcc.Dropdown(
                            id = 'cis',
                            options = [
                                {'label' : 'Yes', 'value' : 1},
                                {'label' : 'No', 'value' : 0}
                            ],
                            value = 0
                        ),

                        #reccurence rate
                        # html.Label('Prior reccurence rate'),
                        # html.Div('Unfortunately, our model supports only primary tumors'),
                        # dcc.Dropdown(
                        #     id = 'recRate',
                        #     options = [
                        #         {'label': 'No prior reccurence', 'value' : 0}
                        #     ],
                        #     value = 0
                        # ),

                        #bcg 
                        html.Label('Was BCG used?'),
                        dcc.Dropdown(
                            id = 'bcg',
                            options = [
                                {'label' : 'yes', 'value' : 1},
                                {'label' : 'no', 'value' : 0}
                            ],
                            value = 0
                        ),

                        html.H5('Calculated clinical scores'),
                        DataTable(
                            id = 'calculatedScores',
                            columns = [{'name' : i, 'id' : i} for i in ['EORTC P score', 'EORTC R score', 'CUETO P score', 'CUETO R score']]    
                        ),

                        html.H5('Survival probability per year'),
                        DataTable(
                            id = 'survivals',
                            columns = [{'name' : i, 'id' : i} for i in ['time [years]', 'PFS (95CI)', 'RFS (95CI)']]
                        )

                        
                    ]),
                ],
            ),
            # dbc.Col(width = 200),
            dbc.Col(
                [
                    html.Div(id = 'resultsArea', children = [

                        html.H4(children = 'Predictions'),
                        dcc.Graph(id = 'figureOutput'),

                        
                        
                    ])
                ]
            )
        ]
    )
])

@app.callback(
    Output(component_id = 'figureOutput', component_property = 'figure'),
    [
        Input(component_id = 'gender', component_property = 'value'),
        Input(component_id = 'age', component_property = 'value'),
        Input(component_id = 't', component_property = 'value'),
        Input(component_id = 'grade', component_property = 'value'),
        Input(component_id = 'tumors', component_property = 'value'),
        Input(component_id = 'diam', component_property = 'value'),
        Input(component_id = 'cis', component_property = 'value'),
        # Input(component_id = 'recRate', component_property = 'value'),
        Input(component_id = 'bcg', component_property = 'value')
    ]
)
def createGraph(gender, age, t, grade, tumors, diam, cis, bcg) :

    #define a layput of returning figure 

    fig = go.Figure(
        layout = go.Layout(
            template = 'simple_white',
            xaxis = dict(
                title = dict(
                    text = 'Survival time [years]'
                ),
                range = [0, 5]
            ),
            yaxis = dict(
                title = dict(
                    text = 'Survival probability'
                ),
                range = [0, 1]
            ),
            hovermode = 'x unified',
            height = 700
        )
    )

    # calculate EORTC and CUETO scales
    recRate = 0
    cuetoR, cuetoP = calculateCUETO(gender, age, tumors, t, cis, grade)
    eortcR, eortcP = calculateEORTC(tumors, diam, recRate, t, cis, grade)

    varList = [gender, age, t, cis, grade, tumors, diam, bcg, eortcR, eortcP, cuetoR, cuetoP]
    
    #run the models
    pfsSet = generateHighRes(pfsMod.predict_survival(varList)[0], pfsMod.times)
    rfsSet = generateHighRes(rfsMod.predict_survival(varList)[0], rfsMod.times)

    #create a figure
    fig.add_trace(go.Scatter(x = pfsSet[0],y = pfsSet[1], name = 'PFS'))
    fig.add_trace(go.Scatter(x = rfsSet[0], y = rfsSet[1], name = 'RFS'))


    return fig

@app.callback( #update table for calcualted scores
    Output(component_id = 'calculatedScores', component_property = 'data'),
    [
        Input(component_id = 'gender', component_property = 'value'),
        Input(component_id = 'age', component_property = 'value'),
        Input(component_id = 't', component_property = 'value'),
        Input(component_id = 'grade', component_property = 'value'),
        Input(component_id = 'tumors', component_property = 'value'),
        Input(component_id = 'diam', component_property = 'value'),
        Input(component_id = 'cis', component_property = 'value'),
        # Input(component_id = 'recRate', component_property = 'value')
        
    ]
)

def displayScores(gender, age, t, grade, tumors, diam, cis) :
    recRate = 0
    cuetoR, cuetoP = calculateCUETO(gender, age, tumors, t, cis, grade)
    eortcR, eortcP = calculateEORTC(tumors, diam, recRate, t, cis, grade)

    ret = pd.DataFrame([[eortcP, eortcR, cuetoP, cuetoR]], columns = ['EORTC P score', 'EORTC R score', 'CUETO P score', 'CUETO R score'])

    return ret.to_dict('records')

@app.callback(
    Output(component_id = 'survivals', component_property = 'data'),
    [
        Input(component_id = 'gender', component_property = 'value'),
        Input(component_id = 'age', component_property = 'value'),
        Input(component_id = 't', component_property = 'value'),
        Input(component_id = 'grade', component_property = 'value'),
        Input(component_id = 'tumors', component_property = 'value'),
        Input(component_id = 'diam', component_property = 'value'),
        Input(component_id = 'cis', component_property = 'value'),
        # Input(component_id = 'recRate', component_property = 'value'),
        Input(component_id = 'bcg', component_property = 'value')
    ]
)

def calculateSurvivals(gender, age, t, grade, tumors, diam, cis, bcg) :
    recRate = 0
    cuetoR, cuetoP = calculateCUETO(gender, age, tumors, t, cis, grade)
    eortcR, eortcP = calculateEORTC(tumors, diam, recRate, t, cis, grade)

    varList = [gender, age, t, cis, grade, tumors, diam, bcg, eortcR, eortcP, cuetoR, cuetoP]

    ret = pd.DataFrame(columns = ['time [years]', 'PFS (95CI)', 'RFS (95CI)'])



    for i in range(1, 6) :

        #calculate PFS 
        pfs = pfsMod.predict_survival(varList, t = i)[0]
        #pfsL = pfsMod.predict_survival_lower(t = i)
        #pfsU = pfsMod.predict_survival_upper(t = i)

        #calcullate RFS
        rfs = rfsMod.predict_survival(varList, t = i)[0]
        #rfsL = rfsMod.predict_survival_lower(t = i)
        #rfsU = rfsMod.predict_survival_upper(t = i)


        tmp = pd.Series(
            [i, '{:.2f}%'.format(pfs * 100), '{:.2f}%'.format(rfs * 100)],
            index = ret.columns
        )

        ret = ret.append(tmp, ignore_index = True)

    return ret.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug = True, host = '0.0.0.0', port = 8888)