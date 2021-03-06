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

    dbc.Row(
        [ dbc.Col([
            html.H2(children = 'Deep learning-based recalibration of CUETO and EORTC prediction tools for recurrence and progression in non-muscle-invasive bladder cancer.'),
            html.H4(children = "Abstract:"),
            html.P("Background: Prediction of recurrence and progression in non-muscle-invasive bladder cancer (NMIBC) remains essential to bladder cancer care. Despite being the standard tools for decision making, the EORTC, EAU, and CUETO risk groups provide moderate performance in predicting recurrence-free (RFS) and progression-free (PFS) survival."),
            html.P("Objective: Develop and externally validate a merged and recalibrated tool for personalized RFS and PFS prediction in patients with primary NMIBC. "),
            html.P("Design, Setting, and Participants: In this retrospective combined cohort data-mining study, the training group consisted of 3570 patients with de novo diagnosed NMIBC from several European countries treated between 1996 and 2007. Tested predictors included: gender, age, T stage, histopathological grading, number of tumors, tumor diameter, EORTC and CUETO scores, and type of intravesical treatment. The developed models were externally validated in an independent cohort of 322 patients from Poland treated between 2005-2015. "),
            html.P("Outcome Measurements and Statistical Analysis: Models were trained using our implementation of proprietary grid search of hyperparameters for Cox proportional hazards deep neural networks (deep learning; DeepSurv). The performance was assessed using Harrell's c-index."),
            html.P("Results and Limitations: Deep-learning-based models, for only surgical and BCG-treated patients, achieved the c-indices of 0.650 for RFS (95%CI:0.649-0.650) and 0.878 for PFS (95%CI:0.873-0.874) in the training group. In the validation group, the c-indices were estimated at 0.651 for RFS (95%CI:0.648-0.654) and 0.881 for PFS (95%CI:0.878-0.885). After the inclusion of patients treated with mitomycin (MMC), the final neural networks achieved a c-index of 0.885 (95%CI:0.885-0.885) for PFS in the training group and 0.876 (95%CI:0.873-0.880) in the validation group. For RFS, the c-indices were 0.6415 (95%CI:0.6412-0.6417) and 0.660 (95%CI:0.657-0.664) for training and validation groups, respectively."),
            html.P("Conclusion: Our new predictive models allow for personalized NMIBC management. They outperformed standard-of-care risk stratification tools and showed no evidence of overfitting.  "),
            html.P("Patient summary: Using advanced artificial intelligence, we have created and validated the new tool to predict early-stage bladder cancer recurrence and progression. The application combines state-of-the-art scales, outperforms them, and is freely available online.")
        ])]
        
    ),

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
                            value = 1
                        ),
                        html.P("Note: Using 'none' additional treatment in high-risk patient (e.g. T1 or G3) can provide biased results. We turned off the prediction of PFS if 'none' additional treatment is given; use RFS instead.", className = "footertext"),

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
                    html.H5('Survival probability per year:'),
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
    
        rfsSet = generateHighRes(rfsMod.predict_survival(varList)[0], rfsMod.times)
        fig.add_trace(go.Scatter(x = rfsSet[0], y = rfsSet[1], name = 'RFS'))

        if bcg != 0 or mmc != 0:
            pfsSet = generateHighRes(pfsMod.predict_survival(varList)[0], pfsMod.times)
            fig.add_trace(go.Scatter(x = pfsSet[0],y = pfsSet[1], name = 'PFS'))
    else:
        varList = [gender, age, t, cis, grade, tumors, diam, bcg, eortcR, eortcP, cuetoR, cuetoP, mmc]
        
        rfsSet = generateHighRes(rfsModMMC.predict_survival(varList)[0], rfsModMMC.times)
        fig.add_trace(go.Scatter(x = rfsSet[0], y = rfsSet[1], name = 'RFS'))

        if bcg != 0 or mmc != 0:
            pfsSet = generateHighRes(pfsModMMC.predict_survival(varList)[0], pfsModMMC.times)
            fig.add_trace(go.Scatter(x = pfsSet[0],y = pfsSet[1], name = 'PFS'))


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
            if bcg == 0 and mmc == 0:
                pfs = ["Biased, use RFS."]
                rfs = rfsMod.predict_survival(varList, t = i)[0]
                tmp = pd.Series(
                [i, pfs, '{:.2f}%'.format(rfs * 100)],
                index = ret.columns
                )
            else:
                pfs = pfsMod.predict_survival(varList, t = i)[0]
                rfs = rfsMod.predict_survival(varList, t = i)[0]
                tmp = pd.Series(
                [i, '{:.2f}%'.format(pfs * 100), '{:.2f}%'.format(rfs * 100)],
                index = ret.columns
                )
            #pfsL = pfsMod.predict_survival_lower(t = i)
            #pfsU = pfsMod.predict_survival_upper(t = i)

            #calcullate RFS
            
            
            #rfsL = rfsMod.predict_survival_lower(t = i)
            #rfsU = rfsMod.predict_survival_upper(t = i)

            ret = ret.append(tmp, ignore_index = True)

    else:
        varList = [gender, age, t, cis, grade, tumors, diam, bcg, eortcR, eortcP, cuetoR, cuetoP, mmc]

        ret = pd.DataFrame(columns = ['time [years]', 'PFS (95CI)', 'RFS (95CI)'])



        for i in range(1, 6) :

            #calculate PFS 
            if bcg == 0 and mmc == 0:
                pfs = ["Biased, use RFS."]
                rfs = rfsModMMC.predict_survival(varList, t = i)[0]
                tmp = pd.Series(
                [i, pfs, '{:.2f}%'.format(rfs * 100)],
                index = ret.columns
                )
            else:
                pfs = pfsModMMC.predict_survival(varList, t = i)[0]
                rfs = rfsModMMC.predict_survival(varList, t = i)[0]
                tmp = pd.Series(
                [i, '{:.2f}%'.format(pfs * 100), '{:.2f}%'.format(rfs * 100)],
                index = ret.columns
                )

            ret = ret.append(tmp, ignore_index = True)

    return ret.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug = True, host = '0.0.0.0', port = 8888)