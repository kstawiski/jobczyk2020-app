# %% [markdown]
# ## testing models import
# %% get models
import torch
import pysurvival as psurv
from pysurvival.models.semi_parametric import NonLinearCoxPHModel
from pysurvival.utils.metrics import concordance_index
import pandas as pd
import numpy as np
import pickle as pi
import matplotlib.pyplot as plt
import plotly.graph_objects as go

#%% load dependencies
from pysurvival.utils import load_model

sampleInput = [1, 67, int(0), int(2), 1, 1, 0, 1, 0, 2, 2]
poorSample = [1, 74, 2, 3, 1, 1, 1, 9, 15, 5, 10]

#models yet to be loaded

#pfsMod = load_model('modelData/PFS_best.zip')
#rfsMod = load_model('modelData/RFS_best.zip')

#pfsTrain = pd.read_csv('../data/training_pfs.csv')
#pfsVal = pd.read_csv('../data/validation_pfs.csv')

#rfsTrain = pd.read_csv('../data/training_rfs.csv')
#rfsVal = pd.read_csv('../data/validation_rfs.csv')

#summ, iterer = pi.load(open('../data/gridSearch.p', 'rb'))


#%% define useful functions

# event_col is the header in the df that represents the 'Event / Status' indicator
# time_col is the header in the df that represents the event time
def dataframe_to_deepsurv_ds(df, event_col = 'Event', time_col = 'Time'):
    # Extract the event and time columns as numpy arrays
    e = df[event_col].values.astype(np.int32)
    t = df[time_col].values.astype(np.float32)

    # Extract the patient's covariates as a numpy array
    x_df = df.drop([event_col, time_col], axis = 1)
    x = x_df.values.astype(np.float32)
    
    # Return the deep surv dataframe
    return {
        'x' : x,
        'e' : e,
        't' : t
    }



# %% [markdown]
# ## Get prediction from the models
# %%
#predict sample PFS for our patient 

haz = pfsMod.predict_hazard(sampleInput)
plt.plot(pfsMod.times, haz[0])

risk = pfsMod.predict_risk(sampleInput)

surv = pfsMod.predict_survival(poorSample)
plt.plot(pfsMod.times, surv[0])


# %%

def generateHighRes(risks, times, res = 0.001, maxTim = 5) :
    
    hrTimes = []
    hrProb = []

    tmpRisk = 1
    iteratorInd = 0

    for i in range(0, int(maxTim / res)) :

        tmpI = i * res
        hrTimes.append(tmpI)
        hrProb.append(tmpRisk)

        if iteratorInd == len(risks) - 1 :
            continue

        if times[iteratorInd + 1] <= tmpI :
            iteratorInd += 1
            tmpRisk = risks[iteratorInd]
        
    
    return [hrTimes, hrProb]

        


# %%

tst = generateHighRes(surv[0], pfsMod.times)
plt.plot(tst[0], tst[1])
# %%

pfsSet = generateHighRes(pfsMod.predict_survival(poorSample)[0], pfsMod.times)
rfsSet = generateHighRes(rfsMod.predict_survival(poorSample)[0], rfsMod.times)

#%% Create a plotly chart 

fig = go.Figure(

    data = [
        go.Scatter(
            x = pfsSet[0],
            y = pfsSet[1],
            name = 'PFS'
        ),
        go.Scatter(
            x = rfsSet[0],
            y = rfsSet[1],
            name = 'RFS'
        )
    ],
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
        hovermode = 'x unified'
    )
)

fig.show()
# %% [markdown]
# ## Develop functions for calculating scores
# %% get the data

ds = pd.read_csv('../data/analysisData/combined.csv')

#add required 'prior reccurence column 
ds['PriorRecurrence'] = 0

#%%

def calculateEORTC_orig(tumN, diam, recRate, category, conCis, grade) :
    rec = 0
    prog = 0

    #number of tumors
    prog += (tumN >=2) * 3
    rec += ((tumN >= 2) * 3) + ((tumN >= 8) * 3) 

    #tumor diameter
    prog += (diam >= 3) * 3
    rec += (diam >= 3) * 3 

    #reccurence rate 
    prog += (recRate != 0) * 2
    rec += ((recRate != 0) + (recRate > 1)) * 2

    # category; assuming Ta = 0 and T1 = 1
    prog += category * 4
    rec += category

    # concurrent cis 
    prog += conCis * 6
    rec += conCis

    # grade 
    prog += (grade == 3) * 5
    rec += grade - 1

    return [rec, prog]

def calculateEORTC(tumN, diam, category, conCis, grade) :
    
    rec = 0
    prog = 0

    #number of tumors
    prog += (tumN * 3)
    rec += (tumN * 3) 

    #tumor diameter
    prog += (diam * 3)
    rec += (diam * 3)

    # category; assuming Ta = 0 and T1 = 1
    prog += category * 4
    rec += category

    # concurrent cis 
    prog += conCis * 6
    rec += conCis

    # grade 
    prog += (grade == 3) * 5
    rec += grade - 1

    return [rec, prog]
# %% test created eortc formula 

for i in ds.index :
    row = ds.loc[i, :]
    rec, prog = calculateEORTC(row['No_tumors'], row['Diameter'], row['T'], row['CIS'], row['Grading'])

    if rec != row['EORTC_R'] or prog != row['EORTC_P'] : 
        print('wa')
        print('Rec: {} vs {}'.format(rec, row['EORTC_R']))
        print('Prog: {} vs {}'.format(prog, row['EORTC_P']))

# %% define CUETO score calculator 

# reverse - engineered - no official documentation found 

def calculateCUETO_orig(gender, age, tumN, stage, conCis, grade) :

    rec = 0
    prog = 0

    #gender
    rec += (gender == 2) * 3
    prog += 0

    #age 
    rec += int(age >= 60) + int(age > 70)
    prog += (age > 70) * 2

    #number of tumors 
    rec += (tumN > 3) * 2
    prog += (tumN > 3)

    #stage 
    rec += 0
    prog += stage * 2

    #concurrent cis 
    rec += conCis * 2
    prog += conCis * 2

    #grade 
    rec += (grade == 2) + (grade == 3) * 3
    prog += (grade == 2) * 2 + (grade == 3) * 6

    return [rec, prog] 

def calculateCUETO(gender, age, tumN, stage, conCis, grade) :

    rec = 0
    prog = 0

    #gender
    rec += (gender * 3)
    prog += 0

    #age 
    rec += int(age >= 60) + int(age > 70)
    prog += (age > 70) * 2

    #number of tumors 
    rec += tumN * 2
    prog += int(tumN)

    #stage 
    rec += 0
    prog += stage * 2

    #concurrent cis 
    rec += conCis * 2
    prog += conCis 

    #grade 
    rec += (grade == 2) + (grade == 3) * 3
    prog += (grade == 2) * 2 + (grade == 3) * 6

    return [rec, prog] 
# %% test created cueto formula 

for i in ds.index :
    row = ds.loc[i, :]
    rec, prog = calculateCUETO(row['Gender'], row['Age'], row['No_tumors'], row['T'] , row['CIS'], row['Grading'])

    if rec != row['CUETO_R'] or prog != row['CUETO_P'] : 
        print('wa')
        print('Rec: {} vs {}'.format(rec, row['CUETO_R']))
        print('Prog: {} vs {}'.format(prog, row['CUETO_P']))
        print(i)
# %%
