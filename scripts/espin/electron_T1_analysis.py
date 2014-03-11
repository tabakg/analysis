import numpy as np
from analysis.lib.m2.ssro import sequence
from analysis.lib.tools import plot
from measurement.lib.tools import toolbox

from matplotlib import pyplot as plt
from analysis.lib.fitting import fit, common


def electron_T1_anal(timestamp=None, measurement_name = ['ssro'],Amplitude = 2./3, T1 = 500, offset = 1./3,do_print = False):
    ''' Function to analyze T1 measurements. Loads the results and fits them to a simple exponential.
    Inputs:
    timestamp: in format yyyymmdd_hhmmss or hhmmss or None.
    measurement_name: list of measurement names
    '''

    if timestamp != None:
        folder = toolbox.data_from_time(timestamp)
    else:
        folder = toolbox.latest_data('T1')

    fit_results = []
    for k in range(0,len(measurement_name)):
        a = sequence.SequenceAnalysis(folder)
        a.get_sweep_pts()
        a.get_readout_results(measurement_name[k])
        a.get_electron_ROC()
        ax = a.plot_result_vs_sweepparam(ret='ax')

        x = a.sweep_pts
        p0, fitfunc, fitfunc_str = common.fit_exp_decay_with_offset(offset, Amplitude, T1)
        y = a.p0

        fit_result = fit.fit1d(x,y, None, p0=p0, fitfunc=fitfunc, do_print=do_print, ret=True)
        plot.plot_fit1d(fit_result, np.linspace(0,x[-1],201), ax=ax, plot_data=False)
        fit_results.append(fit_result)

    return fit_results