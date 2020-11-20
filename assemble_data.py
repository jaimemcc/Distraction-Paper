# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:28:04 2020

@author: admin
"""

import tdt
import xlrd
import csv
import numpy as np
import trompy as tp

import dill

from fx4assembly import *


def loaddata(tdtfile, SigBlue, SigUV):
    
    tdtfile=raw_datafolder+tdtfile
    
    try:
        tmp = tdt.read_block(tdtfile, evtype=['streams'], store=[SigBlue])
        data = getattr(tmp.streams, SigBlue)['data']
        fs = getattr(tmp.streams, SigBlue)['fs']

        tmp = tdt.read_block(tdtfile, evtype=['streams'], store=[SigUV])
        dataUV = getattr(tmp.streams, SigUV)['data']

        ttls = tdt.read_block(tdtfile, evtype=['epocs']).epocs
    except:
        print('Unable to load data properly.')
        data=[]
        dataUV=[]
        ttls=[]
        fs=[]
        
    return data, dataUV, fs, ttls

def process_rat(row_data, sessiontype='dis', get_trialtype=False):
    print('yo there', row_data[2])
    ratdata={}
    ratdata['rat'] = row_data[2]
    
    # gets photometry signals from TDT file and performs correction
    blue, uv, fs, ttls = loaddata(row_data[0], row_data[12], row_data[13])   
    
    # sets start and stop of good signal from values in metafile (entered by hand)
    datarange=[int(np.float(row_data[19])), int(np.float(row_data[20]))]
    
    # first line uses Vaibhav correction, second uses Lerner correction
    # filt = correctforbaseline(blue, uv)
    filt, filt_sd = lerner_correction(blue, uv)
    
    rms = np.sqrt(np.mean(np.square(filt[datarange[0]:datarange[1]])))
    ratdata["rms"] = rms
    print(rms)
    
    # assigns photometry data to output dictionary
    ratdata['blue'] = blue
    ratdata['uv'] = uv
    ratdata['fs'] = fs
    ratdata['filt'] = filt
#    ratdata['z'] = convert2zscore(filt, zrange=[int(np.float(row_data[19])), int(np.float(row_data[20]))])
    ratdata['deltaF'] = filt / rms
    ratdata['tick'] = ttls.Tick.onset
    
    try:
        ratdata['filt_sd'] = filt_sd
    except: pass
    
    # gets licks from ttls
    lick = getattr(ttls, row_data[15])    
    ratdata['licks'] = lick.onset
    ratdata['licks_off'] = lick.offset
    
    # Calculates distractors and whether distracted or not
    ratdata['distractors'] = distractionCalc2(ratdata['licks']) 
    [ratdata['distracted'], ratdata['notdistracted']], ratdata['d_bool_array'], ratdata['pdp'], ratdata['pre_dp']  = distracted_or_not(ratdata['distractors'], ratdata['licks'])
    
    if get_trialtype == True:
        medfile = medfilefolder + row_data[1]
        ratdata["trialtype"] = tp.medfilereader(medfile, varsToExtract=["j"])[1:]
    else:
        ratdata["trialtype"] = []
    
    return ratdata

# declares locations for data and required files
raw_datafolder = 'D:\\DA_and_Reward\\kp259\\THPH1AND2\\tdtfiles\\'
folder = "C:\\Github\\Distraction-Paper\\"
datafolder = folder+"data\\"
medfilefolder = datafolder + "medfiles\\"
xlfile = datafolder+"distraction_photo_metafile.xlsx"
metafile = datafolder+"metafile"
sheetname="THPH1&2Metafile"

# extracts data from metafile
tp.metafilemaker(xlfile, metafile, sheetname=sheetname, fileformat='txt')
rows, header = tp.metafilereader(metafile + '.txt')

# creates lists that include row indexes for last lick,  distraction, and hab days
rows_mod = []
rows_dis = []
rows_hab = []

for idx, row in enumerate(rows):
    if row[5] == 'D0':
        rows_mod.append(idx)
    elif row[5] == 'D1':
        rows_dis.append(idx)
    elif row[5] == 'D2':
        rows_hab.append(idx)

# makes dictionaries that include data for individual rats for each day (e.g.
# modelled day, distraction day, and habituation day)
disDict = {}
modDict = {}
habDict = {}

for idx in rows_mod:       
    ratdata = process_rat(rows[idx])
    modDict[ratdata['rat']] = ratdata

for idx in rows_dis:       
    ratdata = process_rat(rows[idx], get_trialtype=True)
    disDict[ratdata['rat']] = ratdata
    
for idx in rows_hab:       
    ratdata = process_rat(rows[idx], get_trialtype=True)
    habDict[ratdata['rat']] = ratdata
    
# Saves pickle file with three dictionaries that can be used by Kate's old script
# or new scripts for further analysis
    
savefile=True
outputfile=datafolder+'distraction_data.pickle'

if savefile == True:
    pickle_out = open(outputfile, 'wb')
    dill.dump([modDict, disDict, habDict], pickle_out)
    pickle_out.close()





        