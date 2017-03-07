import os, sys
import numpy as np
import h5py
import logging


from matplotlib import pyplot as plt

from analysis.lib import fitting
from analysis.lib.m2.ssro import sequence
from analysis.lib.tools import toolbox
from analysis.lib.fitting import fit,esr
from analysis.lib.tools import plot

### settings
timestamp ='20160226_110144'#None#'20140710_205010' #' #'114103_PulsarD' #YYYYmmddHHMMSS

guess_offset = 1
guess_x0 = 4.027 #2.807
#guess_splitB = 30.
guess_splitN = 2.18e-3
guess_splitC = .8e-3 
guess_width = 4e-3 #0.2e-3
guess_amplitude = 0.3

def analyze_dark_esr(folder, ax=None, **kw):
    if ax == None:
        fig, ax = plt.subplots(1,1)
    ssro_calib_folder = toolbox.latest_data(contains='AdwinSSRO_SSROCalibration')

    a = sequence.SequenceAnalysis(folder)
    a.get_sweep_pts()
    a.get_readout_results('ssro')
    a.get_electron_ROC(ssro_calib_folder=ssro_calib_folder)

    x = a.sweep_pts # convert to MHz
    y = a.p0.reshape(-1)[:]
    a.plot_result_vs_sweepparam(ret=None, name='ssro', ax=ax)

    guess_ctr = x[np.floor(len(x)/2.)]


    fit_result = fit.fit1d(x, y, esr.fit_ESR_gauss, guess_offset,
            guess_amplitude, guess_width, guess_ctr,
            # (2, guess_splitN),
             #(2, guess_splitC),
            # (2, guess_splitB),
            #(3, guess_splitN),
            do_print=True, ret=True, fixed=[])
    
    plot.plot_fit1d(fit_result, np.linspace(min(x), max(x), 1000), ax=ax, plot_data=False, **kw)
       
    ax.set_xlabel('MW frq (GHz)')
    ax.set_ylabel(r'fidelity wrt. $|0\rangle$')
    ax.set_title(a.timestamp+'\n'+a.measurementstring)
    plt.savefig(os.path.join(folder, 'darkesr_analysis.png'),
            format='png')
    return fit_result
### script
if __name__ == '__main__':
    folder= toolbox.latest_data(contains='DarkESR')
    fit_result=analyze_dark_esr(folder)#toolbox.data_from_time(timestamp))#folder)








