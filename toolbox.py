import torch
import pysurvival as psurv
from pysurvival.models.semi_parametric import NonLinearCoxPHModel
from pysurvival.utils.metrics import concordance_index
import pandas as pd
import numpy as np
import pickle as pi
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pysurvival.utils import load_model


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

            # add new record for the same time to preserve Manhattan-like shape
            hrTimes.append(tmpI)
            hrProb.append(tmpRisk)
        
    
    return [hrTimes, hrProb]


def calculateCUETO(gender, age, tumN, stage, conCis, grade) :

    if grade == 0.5:
        grade = 1 

    if grade == 1.5:
        grade = 2

    if grade == 3.01:
        grade = 3
    
    
    rec = 0
    prog = 0

    #gender
    rec += (gender == 0) * 3
    prog += 0

    #age 
    rec += int(age >= 60) + int(age > 70)
    prog += (age > 70) * 2

    #number of tumors 
    rec += tumN * 2
    prog += tumN

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

def calculateEORTC(tumN, diam, recRate, stage, conCis, grade) :
    if grade == 0.5:
        grade = 1 

    if grade == 1.5:
        grade = 2

    if grade == 3.01:
        grade = 3
    
    
    rec = 0
    prog = 0

    #number of tumors
    prog += (tumN * 3)
    rec += (tumN * 3)

    #tumor diameter
    prog += diam * 3
    rec += diam * 3 

    #reccurence rate 
    #prog += (recRate != 0) * 2 assuming no prior reccurence 
    #rec += ((recRate != 0) + (recRate > 1)) * 2


    # stage; assuming Ta = 0 and T1 = 1
    prog += stage * 4
    rec += stage

    # concurrent cis 
    prog += conCis * 6
    rec += conCis

    # grade 
    prog += (grade == 3) * 5
    rec += grade - 1

    return [rec, prog]