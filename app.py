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
pfsModMMC = load_model('modelData/MMCPFS.zip')
rfsModMMC = load_model('modelData/MMCRFS.zip')


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
                        html.H4(children = 'Input patient data:'),
                        html.P("Please enter the values of following parameters: ", className = 'normalny'),
                        html.P(" "),

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
                        html.P(" "),

                        #age
                        html.Label('Age [years]'),
                        dcc.Input(id = 'age', type = 'number', value = 74),
                        html.P(" "),

                        #T
                        html.Label('T stage [numerical]'),
                        dcc.Dropdown(
                            id = 't',
                            options = [
                                {'label' : 'Ta', 'value' : 0},
                                {'label' : 'T1 or CIS', 'value' : 1}
                            ],
                            value = 0
                        ),
                        html.P(" "),

                        #Grading
                        html.Label('Grade'),
                        dcc.Dropdown(
                            id = 'grade',
                            options = [{'label' : i, 'value' : i} for i in [1, 2, 3]],
                            value = 1
                        ),
                        html.P(" "),

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
                        html.P(" "),

                        #diameter
                        html.Label('Diameter [cm]'),
                        dcc.Dropdown(
                            id = 'diam',
                            options = [
                                {'label' : 'Smaller than 3 cm', 'value' : 0},
                                {'label' : '3 cm or bigger', 'value' : 1}
                            ],
                            value = 0
                        ),

                        #concurrent Cis
                        #html.Label('Is concurrent CIS present?'),
                        #dcc.Dropdown(
                        #    id = 'cis',
                        #    options = [
                        #        {'label' : 'Yes', 'value' : 0},
                        #        {'label' : 'No', 'value' : 0}
                        #    ],
                        #    value = 0
                        #),
                        dcc.Input(id = 'cis', type = 'hidden', value = 0),
                        html.P(" "),


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
                        html.Label('Additional treatment?'),
                        dcc.Dropdown(
                            id = 'bcg',
                            options = [
                                {'label' : 'none', 'value' : 0},
                                {'label' : 'BCG', 'value' : 1},
                                {'label' : 'MMC (mitomycin)', 'value' : 2}
                            ],
                            value = 0
                        ),
                        html.P("Note: using 'none' additional treatment in high-risk patient (e.g. T1 or G3) can provide biased results.", className = "footertext"),

                        html.H5('Calculated clinical scores:'),
                        DataTable(
                            id = 'calculatedScores',
                            columns = [{'name' : i, 'id' : i} for i in ['EORTC P score', 'EORTC R score', 'CUETO P score', 'CUETO R score']]    
                        )

                      

                        
                    ]),
                ],
            ),
            # dbc.Col(width = 200),
            dbc.Col(
                [
                    html.Div(id = 'resultsArea', children = [

                        html.H4(children = 'Predictions:'),
                        dcc.Dropdown(
                            id = 'model',
                            options = [
                                {'label' : 'Validated model (for surgery only and BCG-treated patients)', 'value' : 0},
                                {'label' : 'Extended model (also for MMC-treated patients)', 'value' : 1}
                            ],
                            value = 0
                        ),
                        html.P("Note: In 'Validated' model selecting 'MMC' treatment is treated as no additional treatment.", className = "footertext"),


                        dcc.Graph(id = 'figureOutput', className = "wykres"),

                        
                        
                    ]),
                    html.H5('Survival probability per year'),
                        DataTable(
                            id = 'survivals',
                            columns = [{'name' : i, 'id' : i} for i in ['time [years]', 'PFS (95CI)', 'RFS (95CI)']]
                        )
                ]
            )
        ]
    ),

    dbc.Row(
        [
            html.Div(id = 'footer', children = [
                html.Br(),
                html.P("This software is suplemental to paper entitled 'Deep learning-based recalibration of CUETO and EORTC prediction tools for recurrence and progression in non-muscle-invasive bladder cancer.' by Jobczyk et al.", className = 'footertext'),
                html.P("Software authors: Marcin Kaszkowiak, Konrad Stawiski (konrad@konsta.com.pl).", className = 'footertext'),
                html.P("Created by Department of Biostatistics and Translational Medicine @ Medical University of Lodz. | biostat.umed.pl", className = 'footertext')
            ])
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
        Input(component_id = 'bcg', component_property = 'value'),
        Input(component_id = 'model', component_property = 'value')
    ]
)
def createGraph(gender, age, t, grade, tumors, diam, cis, bcg, model) :

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
            height = 400
        )
    )

    # calculate EORTC and CUETO scales
    recRate = 0
    cuetoR, cuetoP = calculateCUETO(gender, age, tumors, t, cis, grade)
    eortcR, eortcP = calculateEORTC(tumors, diam, recRate, t, cis, grade)

    if bcg == 2:
        bcg = 0
        mmc = 1
    else:
        mmc = 0


    if model == 0:
        varList = [gender, age, t, cis, grade, tumors, diam, bcg, eortcR, eortcP, cuetoR, cuetoP]
    
        #run the models
        pfsSet = generateHighRes(pfsMod.predict_survival(varList)[0], pfsMod.times)
        rfsSet = generateHighRes(rfsMod.predict_survival(varList)[0], rfsMod.times)

        #create a figure
        fig.add_trace(go.Scatter(x = pfsSet[0],y = pfsSet[1], name = 'PFS'))
        fig.add_trace(go.Scatter(x = rfsSet[0], y = rfsSet[1], name = 'RFS'))
    else:
        varList = [gender, age, t, cis, grade, tumors, diam, bcg, eortcR, eortcP, cuetoR, cuetoP, mmc]
        
        #run the models
        pfsSet = generateHighRes(pfsModMMC.predict_survival(varList)[0], pfsModMMC.times)
        rfsSet = generateHighRes(rfsModMMC.predict_survival(varList)[0], rfsModMMC.times)

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
        # Input(component_id = 'model', component_property = 'value'),
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
        Input(component_id = 'bcg', component_property = 'value'),
        Input(component_id = 'model', component_property = 'value'),
    ]
)
def calculateSurvivals(gender, age, t, grade, tumors, diam, cis, bcg, model) :
    recRate = 0
    cuetoR, cuetoP = calculateCUETO(gender, age, tumors, t, cis, grade)
    eortcR, eortcP = calculateEORTC(tumors, diam, recRate, t, cis, grade)

    if bcg == 2:
        bcg = 0
        mmc = 1
    else:
        mmc = 0

    if model == 0:
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

    else:
        varList = [gender, age, t, cis, grade, tumors, diam, bcg, eortcR, eortcP, cuetoR, cuetoP, mmc]

        ret = pd.DataFrame(columns = ['time [years]', 'PFS (95CI)', 'RFS (95CI)'])



        for i in range(1, 6) :

            #calculate PFS 
            pfs = pfsModMMC.predict_survival(varList, t = i)[0]
            #pfsL = pfsMod.predict_survival_lower(t = i)
            #pfsU = pfsMod.predict_survival_upper(t = i)

            #calcullate RFS
            rfs = rfsModMMC.predict_survival(varList, t = i)[0]
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