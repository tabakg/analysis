import os, sys
import numpy as np
import h5py
import logging

from matplotlib import pyplot as plt
from analysis.lib import fitting
from analysis.lib.m2.ssro import mbi
from analysis.lib.fitting import fit
from measurement.lib.tools import toolbox
from analysis.lib.m2 import m2
from analysis.lib.m2.ssro import ssro
from analysis.lib.tools import plot

timestamp = None#'20130802145720'

if timestamp != None:
    folder = toolbox.data_from_time(timestamp)
else:
    folder = toolbox.latest_data()

a = sequence.SequenceAnalysis(folder)
a.get_sweep_pts()
a.get_readout_results(name='ssro')
a.get_electron_ROC()
#a.get_N_ROC(1.00, 0.02, 0.94, 0.01, 0.96, 0.01)
ax = a.plot_result_vs_sweepparam(ret='ax', name='ssro')

x = a.sweep_pts.reshape(-1)[:]
y = a.p0.reshape(-1)[:]


# Note: if f is added below, there is a cosine superimposed on the Gaussian.
x0 = fit.Parameter(-0.25, 'x0')
a = fit.Parameter(0.5, 'a')
o = fit.Parameter(0.5, 'o')
c = fit.Parameter(1, 'c')
f = fit.Parameter(1/0.5, 'f')
fitfunc_str = 'o + a * exp( - ( (x-x0)/c )^2) * cos (2 pi f (x-x0))'

def fitfunc(x):
    return o() + a() * np.exp( -((x-x0())/ c())**2) * np.cos(2*np.pi*f()*(x-x0()))

fit_result = fit.fit1d(x,y, None, p0=[o,x0,a,c,f], fixed = [], fitfunc=fitfunc,
        fitfunc_str=fitfunc_str, do_print=True, ret=True)
print fitfunc_str
plot.plot_fit1d(fit_result, np.linspace(x[0],x[-1],201), ax=ax,
        plot_data=False)


