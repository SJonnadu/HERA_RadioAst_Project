#!/usr/bin/env python
# coding: utf-8

# In[5]:


import os
import sys
import numpy as np
import tensorflow as tf
from pyuvdata import UVData
from pyuvdata import UVFlag
from hera_qm.hera_qm import xrfi


# In[6]:


h1c_data = "/lustre/aoc/projects/hera/H1C_IDR2/2458098/zen.2458098.37904.HH.uvh5"
uvd = UVData()
uvd.read_uvh5(h1c_data, antenna_nums=[0, 1])

wf = uvd.get_data(0, 1)

arx = uvd.get_flags(0, 1)

# To read it back in
#uvf_readin = UVFlag('uvflag.h5')
#arx = uvf_readin.flag_array
# is Nblts x Nspw x Nfreq x Npol and is boolean

for x in range (len(arx[0][0])):
    wf_xx = wf[:, :, x]
    if x==0:
        ary = xrfi.xrfi_waterfall(wf_xx)
    else:
        temp = xrfi.xrfi_waterfall(wf_xx)
        ary = np.dstack([ary, temp])         
    x += 1


# In[9]:


def comparision (arx_int, ary_int):
    
    if np.shape(arx) != np.shape(ary):
        raise Exception('Array sizes do not match.')

    arx_int = arx.astype(int)
    ary_int = ary.astype(int)
    
    temp_arr = arx_int + ary_int
    totalcount = arx.size
    true_match = np.count_nonzero(temp_arr==2)
    false_match = np.count_nonzero(temp_arr==0)
    
    temp_arr = arx_int * -1
    temp_arr = temp_arr + ary_int
    tf_match = np.count_nonzero(temp_arr == -1)
    ft_match = np.count_nonzero(temp_arr == 1)
    
    tp = true_match*100/totalcount
    tn = false_match*100/totalcount
    fp = tf_match*100/totalcount
    fn = ft_match*100/totalcount

# Calculate F2 Score
    f2score = 0
    prec_d = tp + fp
    rec_d = tp + fn  
    if prec_d > 0 and rec_d > 0:
        precision = tp/(1.*prec_d)
        recall = tp/(1.*rec_d)
        f2score = 5.*precision*recall/(4.*precision+recall)

# Calculate MCC
    MCC = 0
    if tp==0 and fn ==0:
        MCC = (tp*tn - fp*fn)
    else:
        MCC_d = (tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)
        if MCC_d > 0:
            MCC = (tp*tn - fp*fn)/np.sqrt((1.*MCC_d))
    
    return (f2score, MCC, tp, tn, fp, fn)


# In[10]:


f2score, MCC, true_match, false_match, tf_match, ft_match = comparision(arx, ary)

print("F2 Score: ", "%.2f" % f2score)
print("MCC: ", "%.2f" % MCC)
print("True_x/True_y match: ", "%.2f" % true_match, "%")
print("False_x/False_y match: ", "%.2f" % false_match, "%")
print("True_x/False_y match: ", "%.2f" % tf_match, "%")
print("False_x/True_y match: ", "%.2f" % ft_match, "%")    


# In[ ]:




