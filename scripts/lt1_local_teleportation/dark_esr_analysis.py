import os, sys
import numpy as np
import h5py
import logging

from matplotlib import pyplot as plt

from analysis.lib import fitting
from analysis.lib.m2.ssro import sequence_ssro
from measurement.lib.tools import toolbox
from analysis.lib.fitting import fit, esr
from analysis.lib.tools import plot

### settings
timestamp = None # 
guess_offset = 0.925
guess_ctr = 2863
guess_splitB = 30.
guess_splitN = 2.184
guess_splitC = 12.78
guess_width = 0.2
guess_amplitude = 0.12


### script
if timestamp != None:
    folder = toolbox.data_from_time(timestamp)
else:
    folder = toolbox.latest_data('DarkESR')

a = sequence_ssro.DarkESRAnalysis(folder)
x = a.get_sweep_pts() / 1e6
y = a.get_readout_results()

# try fitting
fit_result = fit.fit1d(x, y, esr.fit_ESR_gauss, guess_offset,
        guess_amplitude, guess_width, guess_ctr,
        (3, guess_splitN),
        # (2, guess_splitB), (2, guess_splitC), (3, guess_splitN), 
        do_print=True, ret=True, fixed=[4])
ax = plot.plot_fit1d(fit_result, x, ret='ax', plot_data=True)

ax.set_xlabel('MW frq (MHz)')
ax.set_ylabel(r'uncorrected fidelity $F(|0\rangle)$')
ax.set_title(a.timestamp+'\n'+a.measurementstring)

plt.savefig(os.path.join(folder, 'darkesr_analysis.pdf'), 
        format='pdf')





