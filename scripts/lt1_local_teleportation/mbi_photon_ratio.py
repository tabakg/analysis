import os
import numpy as np
from matplotlib import pyplot as plt
import h5py
from measurement.lib.tools import toolbox

fn = r'd:\measuring\data\20130219\195325_AdwinSSRO_SIL2_Ex_5nW\analysis.hdf5'


fn = os.path.join(toolbox.latest_data('SSRO'), 'analysis.hdf5')
f = h5py.File(fn, 'r')

pi_inv_prob = 0.6
noof_states = 6

f0data = f['/fidelity/ms0']
f1data = f['/fidelity/ms1']

p0 = f0data[:,1]
p1 = 1-f1data[:,1]
t = f['/fidelity/time']


pop0 = 1./noof_states * pi_inv_prob
pop1 = 1. - pop0
p_prj0 = pop0 * p0 / (pop0*p0 + pop1*p1)

fig = plt.figure(figsize=(8,4))
ax = fig.add_subplot(111)

ax.plot(t[1:], p_prj0[1:], 'o-')
ax.set_xlabel('time (us)')
ax.set_ylabel('probability for projection into 0')
ax.set_xlim(0,50)
ax.set_title('F(MBI)\n$F(\pi) = %.2f$' % pi_inv_prob)
