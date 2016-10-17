"""
Script to analyze the C13 T2 data
Averages over postive and negative electron RO
MAB 2014-01-05
"""

import numpy as np
import os, sys
if os.name == 'posix':
    sys.path.append("/Users/"+os.getlogin()+"/Documents/teamdiamond/")
else:
    sys.path.append("/measuring/")
from analysis.lib.tools import plot, toolbox
from analysis.lib.fitting import fit, common
from analysis.lib.m2.ssro import mbi
from matplotlib import pyplot as plt
reload(common)


def Carbon_T2_analysis(measurement_name = ['adwindata'], ssro_calib_timestamp =None, 
            offset = 0.5, 
            amplitude = 0.5,  
            decay_constant = 0.2, 
            x0=0,
            exponent = 1, 
            Addressed_carbon=5,
            plot_fit = True, do_print = True, show_guess = False):
    ''' 
    Function to gather and analyze T1 measurements of a specific carbon.

    Addressed_carbon: selects the used timestamps and therefore the analyzed carbon

    measurement_name: list of measurement names

    Possible inputs for initial guesses: offset, amplitude, decay_constant,exponent
    '''

    #general plot parameters
    ylim=(0.5,1.0)
    figsize=(6,4.7)



    ######################################
    #    carbon_init= up el_state=0      #
    ######################################

    
    
    if Addressed_carbon == 5:
<<<<<<< HEAD
        timestamp_pos=['20150315_215418']
        timestamp_neg=['20150315_225753']
        timestamp_pos=['20150317_103608']
        timestamp_neg=['20150317_105622']
    elif Addressed_carbon == 1:  
        timestamp_pos=['20150316_000112']
        timestamp_neg=['20150316_010415']
        timestamp_pos=['20150317_015434']
        timestamp_neg=['20150317_021428']
    elif Addressed_carbon == 2:
        timestamp_pos=['20150316_020808']
        timestamp_neg=['20150316_031102']
        timestamp_pos=['20150317_061458']
        timestamp_neg=['20150317_063658']
=======
        timestamp_pos=['20150102_185838']
        timestamp_neg=['20150102_191030']


    else:
        print "Carbon not measured"

    if ssro_calib_timestamp == None: 
        ssro_calib_folder = toolbox.latest_data('SSRO')
    else:
        ssro_dstmp, ssro_tstmp = toolbox.verify_timestamp(ssro_calib_timestamp)
        ssro_calib_folder = toolbox.datadir + '/'+ssro_dstmp+'/'+ssro_tstmp+'_AdwinSSRO_SSROCalibration_111_1_sil18'
        print ssro_calib_folder


    ##accumulate data and average over positive and negative RO##

    cum_pts = 0

    for kk in range(len(timestamp_pos)):
        folder_pos = toolbox.data_from_time(timestamp_pos[kk])
        folder_neg = toolbox.data_from_time(timestamp_neg[kk])
        print folder_pos
        print folder_neg
        a = mbi.MBIAnalysis(folder_pos)
        a.get_sweep_pts()
        a.get_readout_results(name='adwindata')
        timestamp_SSRO, ssro_calib_folder = toolbox.latest_data('AdwinSSRO', older_than = timestamp_pos[kk], return_timestamp = True)
        a.get_electron_ROC(ssro_calib_folder)
        cum_pts += a.pts

        b = mbi.MBIAnalysis(folder_neg)
        b.get_sweep_pts()
        b.get_readout_results(name='adwindata')
        timestamp_SSRO, ssro_calib_folder = toolbox.latest_data('AdwinSSRO', older_than = timestamp_neg[kk], return_timestamp = True)
        b.get_electron_ROC(ssro_calib_folder)

        if kk == 0:
            cum_sweep_pts = a.sweep_pts
            cum_p0 = (a.p0+(1-b.p0))/2.
            cum_u_p0 = np.sqrt(a.u_p0**2+b.u_p0**2)/2
        else:
            cum_sweep_pts = np.concatenate((cum_sweep_pts, a.sweep_pts))
            cum_p0 = np.concatenate((cum_p0, (a.p0+(1-b.p0))/2))
            cum_u_p0 = np.concatenate((cum_u_p0, np.sqrt(a.u_p0**2+b.u_p0**2)/2))

    a.pts   = cum_pts
    a.sweep_pts = cum_sweep_pts
    a.p0    = cum_p0
    a.u_p0  = cum_u_p0


    ## accumulate data with negative RO


    
    #sort data by free evolution time.
    sorting_order=a.sweep_pts.argsort()
    a.sweep_pts.sort()
    a.p0=a.p0[sorting_order]
    a.u_p0=a.u_p0[sorting_order]


    ## generate plot of the raw data ##


    #uncomment this part to plot without error bars, but including obtained fit parameters.
    # fig = a.default_fig(figsize=(6,5))
    # ax = a.default_ax(fig)
    # ax.plot(a.sweep_pts, a.p0, 'bo',label='T1 of Carbon'+str(Addressed_carbon),lw=1.2)


    ax=a.plot_results_vs_sweepparam(ret='ax',ax=None, 
                                    figsize=figsize, 
                                    ylim=(0.4,1.0)
                                    )


    ## fit to a general exponential##

    fit_results = []

    x = a.sweep_pts.reshape(-1)[:]
    y = a.p0.reshape(-1)[:]

    ax.plot(x,y)
    p0, fitfunc, fitfunc_str = common.fit_general_exponential(offset, amplitude, x0, decay_constant,exponent)
    #p0, fitfunc, fitfunc_str = common.fit_line(0.5,-0.5/7.)

    #plot the initial guess

    if show_guess:
        ax.plot(np.linspace(x[0],x[-1],201), fitfunc(np.linspace(x[0],x[-1],201)), ':', lw=2)

    fit_result = fit.fit1d(x,y, None, p0=p0, fitfunc=fitfunc, do_print=True, ret=True,fixed=[0,2])

    ## plot data and fit as function of total time

    if plot_fit == True:
        plot.plot_fit1d(fit_result, np.linspace(x[0],x[-1],1001), ax=ax, plot_data=False)

    fit_results.append(fit_result)

    filename= 'C13_T2_analysis_up_C'+str(Addressed_carbon)
    print 'plots are saved in ' + folder_pos

    #configure the plot
    plt.title('Sample_111_No1_C13_T2_up_C'+str(Addressed_carbon)+'el_state_0')
    plt.xlabel('Free evolution time (s)')
    plt.ylabel('Fidelity')
    plt.axis([a.sweep_pts[0],a.sweep_pts[a.pts-1],0.4,1.])


    plt.savefig(os.path.join(folder_pos, filename+'.pdf'),
    format='pdf')
    plt.savefig(os.path.join(folder_pos, filename+'.png'),
    format='png')


    ######################################
    #    carbon_init= up el_state=1      #
    ######################################


    if Addressed_carbon == 5:

        timestamp_pos=['20150315_231309']#First
        timestamp_neg=['20150315_220943']#First
        timestamp_neg=['20150317_111643']#No shutter
        timestamp_pos=['20150317_120932']#No shutter
        # timestamp_neg=['20150317_084219']#Shutter
        # timestamp_pos=['20150317_093928']#Shutter
    elif Addressed_carbon == 1:
        timestamp_pos=['20150316_012016']
        timestamp_neg=['20150316_001620']
        timestamp_neg=['20150317_023359']#No shutter
        timestamp_pos=['20150317_032742']#No shutter
        timestamp_neg=['20150317_000109']#Shutter
        timestamp_pos=['20150317_005741']#Shutter
    elif Addressed_carbon == 2:
        timestamp_pos=['20150316_032609']
        timestamp_neg=['20150316_022328']
        timestamp_neg=['20150317_065552']#No shutter
        timestamp_pos=['20150317_074908']#No shutter
        # timestamp_neg=['20150317_042104']#Shutter
        # timestamp_pos=['20150317_051738']#Shutter
        # timestamp_pos=['20150102_192226']
        # timestamp_neg=['20150102_214323']
        timestamp_neg=['20150310_191115']
        timestamp_pos=['20150310_195806']
        
    else:
        print "Carbon not measured"
   
    if ssro_calib_timestamp == None: 
        ssro_calib_folder = toolbox.latest_data('SSRO')
    else:
        ssro_dstmp, ssro_tstmp = toolbox.verify_timestamp(ssro_calib_timestamp)
        ssro_calib_folder = toolbox.datadir + '/'+ssro_dstmp+'/'+ssro_tstmp+'_AdwinSSRO_SSROCalibration_111_1_sil18'
        print ssro_calib_folder


    ##accumulate data and average over positive and negative RO##

    cum_pts = 0

    for kk in range(len(timestamp_pos)):
        folder_pos = toolbox.data_from_time(timestamp_pos[kk])
        folder_neg = toolbox.data_from_time(timestamp_neg[kk])
        a = mbi.MBIAnalysis(folder_pos)
        a.get_sweep_pts()
        a.get_readout_results(name='adwindata')
        timestamp_SSRO, ssro_calib_folder = toolbox.latest_data('AdwinSSRO', older_than = timestamp_pos[kk], return_timestamp = True)
        a.get_electron_ROC(ssro_calib_folder)
        cum_pts += a.pts

        b = mbi.MBIAnalysis(folder_neg)
        b.get_sweep_pts()
        b.get_readout_results(name='adwindata')
        timestamp_SSRO, ssro_calib_folder = toolbox.latest_data('AdwinSSRO', older_than = timestamp_neg[kk], return_timestamp = True)
        b.get_electron_ROC(ssro_calib_folder)

        if kk == 0:
            cum_sweep_pts = a.sweep_pts
            cum_p0 = (a.p0+(1-b.p0))/2.
            cum_u_p0 = np.sqrt(a.u_p0**2+b.u_p0**2)/2
        else:
            cum_sweep_pts = np.concatenate((cum_sweep_pts, a.sweep_pts))
            cum_p0 = np.concatenate((cum_p0, (a.p0+(1-b.p0))/2))
            cum_u_p0 = np.concatenate((cum_u_p0, np.sqrt(a.u_p0**2+b.u_p0**2)/2))
            print

    a.pts   = cum_pts
    a.sweep_pts = cum_sweep_pts
    a.p0    = cum_p0
    a.u_p0  = cum_u_p0


    ## accumulate data with negative RO


    
    #sort data by free evolution time.
    sorting_order=a.sweep_pts.argsort()
    a.sweep_pts.sort()
    a.p0=a.p0[sorting_order]
    a.u_p0=a.u_p0[sorting_order]


    ## generate plot of the raw data ##


    #uncomment this part to plot without error bars, but including obtained fit parameters.
    # fig = a.default_fig(figsize=(6,5))
    # ax = a.default_ax(fig)
    # ax.plot(a.sweep_pts, a.p0, 'bo',label='T1 of Carbon'+str(Addressed_carbon),lw=1.2)


    ax=a.plot_results_vs_sweepparam(ret='ax',figsize=figsize, ax=None, ylim=ylim)
    ## fit to a general exponential##

    fit_results = []

    x = a.sweep_pts.reshape(-1)[:]
    y = a.p0.reshape(-1)[:]

    ax.plot(x,y)
    p0, fitfunc, fitfunc_str = common.fit_general_exponential(offset, amplitude, x0, decay_constant,exponent)
    #p0, fitfunc, fitfunc_str = common.fit_line(0.5,-0.5/7.)

    #plot the initial guess

    if show_guess:
        ax.plot(np.linspace(x[0],x[-1],201), fitfunc(np.linspace(x[0],x[-1],201)), ':', lw=2)

    fit_result = fit.fit1d(x,y, None, p0=p0, fitfunc=fitfunc, do_print=True, ret=True,fixed=[0,2])

    ## plot data and fit as function of total time

    if plot_fit == True:
        plot.plot_fit1d(fit_result, np.linspace(x[0],x[-1],1001), ax=ax, plot_data=False)

    fit_results.append(fit_result)

    filename= 'C13_T2_analysis_up_C'+str(Addressed_carbon)
    print 'plots are saved in ' + folder_pos

    #configure the plot
    plt.title('Sample_111_No1_C13_T2_up_C'+str(Addressed_carbon)+'el_state_1')
    plt.xlabel('Free evolution time (s)')
    plt.ylabel('Fidelity')
    plt.axis([a.sweep_pts[0],a.sweep_pts[a.pts-1],0.4,1])


    plt.savefig(os.path.join(folder_pos, filename+'.pdf'),
    format='pdf')
    plt.savefig(os.path.join(folder_pos, filename+'.png'),
    format='png')




<<<<<<< HEAD
Carbon_T2_analysis(Addressed_carbon=1, 
           amplitude = 0.4, show_guess=False)
=======
Carbon_T2_analysis(Addressed_carbon=5, ssro_calib_timestamp ='20150102_153923', 
<<<<<<< Updated upstream
            amplitude = 0.4, show_guess=False)
=======
            amplitude = 0.4, show_guess=False)
>>>>>>> origin/master
>>>>>>> Stashed changes
