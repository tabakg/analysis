'''
Script to analyze the dynamical decoupling data
'''
import numpy as np
import os
# import analysis.lib.QEC.nuclear_spin_characterisation as SC #used for simulating FP response of spins
import matplotlib.cm as cm
from matplotlib import pyplot as plt

# Nothing changed wrt fp_funcs in QEC_analysis
import fp_purification_funcs as fp_funcs; reload(fp_funcs)

import nuclear_spin_char as SC;  reload(SC)

def fingerprint(disp_sim_spin = True,xlim=None,xticks=0.5):
    
    ###################
    ## Data location ##
    ###################
    
    timestamp ='20160112_234557'#'20160111_165950'#
    ssro_calib_folder = 'd:\\measuring\\data\\20160107\\172632_AdwinSSRO_SSROCalibration_Pippin_SIL1'
    a, folder = fp_funcs.load_mult_dat(timestamp, 
              number_of_msmts = 120,
              x_axis_step     = 0.1,
              x_axis_start    = 3.5,
              x_axis_pts_per_msmnt= 51,
              ssro_calib_folder=ssro_calib_folder)


    #######################
    # Add simulated spins #
    #######################

    if disp_sim_spin == True:
            
            print 'Starting Simulation'  
            HF_perp, HF_par = fp_funcs.get_hyperfine_params(ms = 'min', NV = 'Pippin')
            print 'HF_perp = ' + str(HF_perp)
            print 'HF_par = ' + str(HF_par)
            B_Field = 417.268
            tau_lst = np.linspace(0, 72e-6, 10000)
            Mt16 = SC.dyn_dec_signal(HFs_par = HF_par, HFs_orth = HF_perp,
              B_field = B_Field, N = 64, tau = tau_lst)
            FP_signal16 = ((Mt16+1)/2)
 
    ###############
    ## Plotting ###
    ###############

    fig = a.default_fig(figsize=(35,5))
    ax = a.default_ax(fig)
    if xlim == None:
        ax.set_xlim(3.5,15.5)
    else:
        ax.set_xlim(xlim)
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, xticks))

    ax.set_ylim(-0.05,1.05)
    print a.sweep_pts
    ax.plot(a.sweep_pts, a.p0, '.-k', lw=0.4,label = 'data') #N = 16
    # ax.plot(b.sweep_pts, b.p0, '.-b', lw=0.4,label = 'data') #N = 16

    if disp_sim_spin == True:
      colors = cm.rainbow(np.linspace(0, 1, len(HF_par)))
      for tt in range(len(HF_par)):
        ax.plot(tau_lst*1e6, FP_signal16[tt,:] ,'-',lw=.8,label = 'spin' + str(tt+1), color = colors[tt])
    
    # # lOOK AT THIS PART. SEEMS TO HAVE NO FUNCTION
    # if False:
    #     tot_signal = np.ones(len(tau_lst))
    #     for tt in range(len(HF_par)):
    #       tot_signal = tot_signal * Mt16[tt,:]
    #     fin_signal = (tot_signal+1)/2.0   
    #     ax.plot(tau_lst*1e6, fin_signal,':g',lw=.8,label = 'tot')
    

    plt.legend(loc=4)

    print folder
    plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint.pdf'),
        format='pdf')
    plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint.png'),
        format='png')

