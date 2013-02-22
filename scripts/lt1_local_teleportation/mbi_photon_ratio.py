import numpy as np
from matplotlib import pyplot as plt
import h5py

fn = r'/Users/wp/Dropbox/Teleportation/Experiments/2013-01.. nuclei phases lt1-sil3/01 ssro/20130212/191358_AdwinSSRO_SIL3_Ey_5nW/analysis.hdf5'
f = h5py.File(fn, 'r')

pi_inv_prob = 0.95
noof_states = 12

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
ax.set_ylabel('$P_{MBI}$')
ax.set_xlim(0,50)
# ax.set_title('F(MBI)\n$F(\pi) = %.2f$' % pi_inv_prob)
