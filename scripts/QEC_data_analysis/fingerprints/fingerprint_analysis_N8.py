'''
Module to analyze the dynamical decoupling data for N=8, ms=+1 and ~300 Gauss
'''

import numpy as np
from analysis.lib.tools import toolbox
from analysis.lib.m2.ssro import mbi
import analysis.lib.QEC.nuclear_spin_characterisation as SC 
import matplotlib.cm as cm
import os
from matplotlib import pyplot as plt

import analysis.lib.QEC.hyperfine_params as module_hyperfine_params; reload(module_hyperfine_params) 
hf = module_hyperfine_params.hyperfine_params_hans_SIL1_msm1

import fingerprint_funcs as fp_funcs; reload(fp_funcs)


def fingerprint(disp_sim_spin = True):
    ###################
    # Add simulated spins #
    ###################

    if disp_sim_spin == True:
            HF_par =   [hf['C1']['par'],hf['C2']['par'],hf['C3']['par'], hf['C4']['par'], hf['C5']['par'], hf['C6']['par'], hf['C7']['par'], hf['C8']['par'], hf['C9']['par'], hf['C10']['par'],   hf['C11']['par'],  hf['C12']['par']]
            HF_perp =   [hf['C1']['perp'],hf['C2']['perp'],hf['C3']['perp'], hf['C4']['perp'], hf['C5']['perp'], hf['C6']['perp'], hf['C7']['perp'], hf['C8']['perp'], hf['C9']['perp'], hf['C10']['perp'],   hf['C11']['perp'],  hf['C12']['par']]
          
            B_Field = 304.12 # use magnet tools  Bz = (msp1_f**2 - msm1_f**2)/(4.*ZFS*g_factor)

            tau_lst = np.linspace(0,72e-6,10000)
            Mt16 = SC.dyn_dec_signal(HF_par,HF_perp,B_Field,8,tau_lst)
            FP_signal16 = ((Mt16+1)/2)

    ## Data location ##
    timestamp ='20140420_110552'
    ssro_calib_folder = 'D:\\measuring\data\\20140420\\104001_AdwinSSRO_SSROCalibration_Hans_sil1'
    a, folder = load_mult_dat(timestamp, number_of_msmts = 164, ssro_calib_folder=ssro_calib_folder)
 
    ############
    ## Plotting ###
    ############

    fig = a.default_fig(figsize=(35,5))
    ax = a.default_ax(fig)
    ax.set_xlim(0,20)
    start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, 0.5))

    ax.set_ylim(-0.05,1.05)
   
    ax.plot(a.sweep_pts, a.p0, '.-k', lw=0.4,label = 'data') #N = 16
    
    if disp_sim_spin == True:
      colors = cm.rainbow(np.linspace(0, 1, len(HF_par)))
      for tt in range(len(HF_par)):
        ax.plot(tau_lst*1e6, FP_signal16[tt,:] ,'-',lw=.8,label = 'spin' + str(tt+1), color = colors[tt])
    if False:
        tot_signal = np.ones(len(tau_lst))
        for tt in range(len(HF_par)):
          tot_signal = tot_signal * Mt16[tt,:]
        fin_signal = (tot_signal+1)/2.0   
        ax.plot(tau_lst*1e6, fin_signal,':g',lw=.8,label = 'tot')
    

    plt.legend(loc=4)

    print folder
    plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint_short.pdf'),
        format='pdf')
    plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint_short.png'),
        format='png')

    

    ### Julia, can we delete all this below, or does it contain usefull code? ###

    # fig = a.default_fig(figsize=(35,5))
    # ax = a.default_ax(fig)
    # # ax.set_xlim(15.0,15.5)
    # ax.set_xlim(50,70)
    # start, end = ax.get_xlim()
    # ax.xaxis.set_ticks(np.arange(start, end, 0.5))

    # ax.set_ylim(-0.05,1.05)
   
    # ax.plot(a.sweep_pts, a.p0, '.-k', lw=0.4,label = 'data') #N = 16
    
    # if disp_sim_spin == True:
    #   colors = cm.rainbow(np.linspace(0, 1, len(HF_par)))
    #   for tt in range(len(HF_par)):
    #     ax.plot(tau_lst*1e6, FP_signal16[tt,:] ,'-',lw=.8,label = 'spin' + str(tt+1), color = colors[tt])
    # if False:
    #     tot_signal = np.ones(len(tau_lst))
    #     for tt in range(len(HF_par)):
    #       tot_signal = tot_signal * Mt16[tt,:]
    #     fin_signal = (tot_signal+1)/2.0   
    #     ax.plot(tau_lst*1e6, fin_signal,':g',lw=.8,label = 'tot')
    

    # plt.legend(loc=4)

    # print folder
    # plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint_short2.pdf'),
    #     format='pdf')
    # plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint_short2.png'),
    #     format='png')

    # fig = a.default_fig(figsize=(10,5))
    # ax = a.default_ax(fig)
    # # ax.set_xlim(15.0,15.5)
    # ax.set_xlim(6,13)
    # start, end = ax.get_xlim()
    # ax.xaxis.set_ticks(np.arange(start, end, 0.5))

    # ax.set_ylim(-0.05,1.05)
   
    # ax.plot(a.sweep_pts, a.p0, '.-k', lw=0.4,label = 'data',color='green') #N = 16
    
    # if disp_sim_spin == True:
    #   colors = cm.rainbow(np.linspace(0, 1, len(HF_par)))
    #   for tt in range(len(HF_par)):
    #     ax.plot(tau_lst*1e6, FP_signal16[tt,:] ,'-',lw=.8,label = 'spin' + str(tt+1), color = colors[tt])
    # if False:
    #     tot_signal = np.ones(len(tau_lst))
    #     for tt in range(len(HF_par)):
    #       tot_signal = tot_signal * Mt16[tt,:]
    #     fin_signal = (tot_signal+1)/2.0   
    #     ax.plot(tau_lst*1e6, fin_signal,':g',lw=.8,label = 'tot',color='blue')
    

    # plt.legend(loc=4)

    # print folder
    # plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint_vshort.pdf'),
    #     format='pdf')
    # plt.savefig(os.path.join(folder, str(disp_sim_spin)+'fingerprint_vshort.png'),
    #     format='png')


def load_mult_dat(timestamp, number_of_msmts, ssro_calib_folder=''):
   cum_pts = 0
   for kk in range(number_of_msmts):
       folder = toolbox.data_from_time(timestamp)
       a = mbi.MBIAnalysis(folder)
       a.get_sweep_pts()
       a.get_readout_results(name='measurement' + str(kk))
       a.get_electron_ROC(ssro_calib_folder=ssro_calib_folder)
       cum_pts += a.pts

       if kk == 0:
           cum_sweep_pts = np.linspace(2.0, 2.5, 51)#a.sweep_pts
           cum_p0 = a.p0
           cum_u_p0 = a.u_p0
       else:
           cum_sweep_pts = np.concatenate((cum_sweep_pts, np.linspace(2.0+kk*(50)*10e-3, 2.5+kk*(50)*10e-3, 51)))
           cum_p0 = np.concatenate((cum_p0, a.p0))
           cum_u_p0 = np.concatenate((cum_u_p0, a.u_p0))

   a.pts   = cum_pts
   a.sweep_pts = cum_sweep_pts
   a.p0    = cum_p0
   a.u_p0  = cum_u_p0

   return a, folder