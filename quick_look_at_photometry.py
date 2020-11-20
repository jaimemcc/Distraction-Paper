# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 13:21:40 2020

@author: admin
"""

import tdt
import matplotlib.pyplot as plt

folder = 'D:\\DA_and_Reward\\kp259\\THPH1AND2\\tdtfiles\\'
tdtfile = "Kate-170620-090315"


SigBlue1 = "Dv1A"

# SigBlue1 = "Dv1B"
# SigBlue2 = "Dv3B"

tmp = tdt.read_block(folder+tdtfile, evtype=['streams'], store=[SigBlue1])
data = getattr(tmp.streams, SigBlue1)['data']

plt.plot(data)

try:
    tmp = tdt.read_block(folder+tdtfile, evtype=['streams'], store=[SigBlue2])
    data = getattr(tmp.streams, SigBlue2)['data']
    
    plt.plot(data)
except:
    print("No second channel")
# plt.plot(data[87328:3650000])