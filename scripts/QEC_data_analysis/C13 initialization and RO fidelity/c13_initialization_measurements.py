import numpy as np
import os
from analysis.lib.tools import toolbox; reload(toolbox)
from analysis.lib.tools import plot; reload(plot)
from analysis.lib.fitting import fit, common, ramsey;reload(common); reload(fit) 
from analysis.lib.m2.ssro import mbi
from matplotlib import pyplot as plt

''' Script to analyze and fit the electron Ramsey data with 13C initialization, 
    as well as the simultaneously taken tomography data THT 141201 ''' 

''' Plan: 
- We then want to fit this data with a model that gives us the initialization fidelity
'''

### Data folders

    ### First data set
# timestamp_list_noinit = ['20141201_192629', '20141201_194015', '20141201_195413', '20141201_201324', '20141201_202722', '20141201_204121',
#                         '20141201_211401', '20141201_212807'] 
# timestamp_list_up =     ['20141201_191556', '20141201_192955', '20141201_194338', '20141201_200247', '20141201_201647', '20141201_203051',
#                         '20141201_210314', '20141201_211722'] 
# timestamp_list_down =   ['20141201_192115', '20141201_193458',  '20141201_194859', '20141201_200759', '20141201_202211', '20141201_203606',
#                         '20141201_210831', '20141201_212240'] 

    ### Second data set
''' 
Carbons    : C1, C2, C5 
older_than : 20141202_092002 
'''

ssro_calib_folder = 'D:\\measuring\data\\20141201\\114408_AdwinSSRO_SSROCalibration_111_1_sil18'

def get_and_plot_data(timestamp_list, ssro_calib_folder):

    for ii, timestamp in enumerate(timestamp_list):

        folder = toolbox.data_from_time(timestamp)
        
        a = mbi.MBIAnalysis(folder)
        a.get_sweep_pts()
        a.get_readout_results(name='adwindata')
        a.get_electron_ROC(ssro_calib_folder)
        
        # if ii==0:
        #     ax = a.plot_results_vs_sweepparam(ret='ax', markersize = 4, save=False, fmt = 'o-')
        #     ax.set_ylim(-0.05,1.05)
        #     ax.set_xlim(a.sweep_pts[0],a.sweep_pts[-1])
        #     ax.axhspan(0,1,fill=False,ls='dotted')
        #     ax.axhspan(0,0.5,fill=False,ls='dotted')
        # else: 
        #     a.plot_results_vs_sweepparam(ax= ax,  markersize = 4, save=False, fmt = 'o-')
        
        if ii==0:
            p0_sum     = a.p0
            u_p0_sum   = a.u_p0**2 
        else:
            p0_sum     = p0_sum + a.p0
            u_p0_sum   = u_p0_sum + a.u_p0**2
    
    a.p0   = p0_sum/len(timestamp_list) 
    a.u_p0 = (u_p0_sum**0.5) / len(timestamp_list) 
    
    a.x    = a.sweep_pts.reshape(-1)[:]
    a.p0   = a.p0.reshape(-1)[:]
    a.u_p0 = a.u_p0.reshape(-1)[:] 

    return a, folder

def get_and_plot_data_nuc_RO(timestamp_list_pos, timestamp_list_neg, ssro_calib_folder):

    for ii, timestamp in enumerate(timestamp_list_pos):

        folder = toolbox.data_from_time(timestamp)
        a = mbi.MBIAnalysis(folder)
        a.get_sweep_pts()
        a.get_readout_results(name='adwindata')
        a.get_electron_ROC(ssro_calib_folder)
        a.x    = a.sweep_pts.reshape(-1)[:]
        a.sweep_pts = range(len(a.p0))
        
        folder = toolbox.data_from_time(timestamp_list_neg[ii])
        b = mbi.MBIAnalysis(folder)
        b.get_sweep_pts()
        b.get_readout_results(name='adwindata')
        b.get_electron_ROC(ssro_calib_folder)
        
        ### Combine positive/negative data
        a.p0 = ( (2*a.p0-1) - (2*b.p0-1))/2.
        a.u_p0 =  (a.u_p0**2 + a.u_p0**2)**0.5 

        if ii==0:
            ax = a.plot_results_vs_sweepparam(ret='ax', markersize = 4, save=False, fmt = 'o')
            ax.set_ylim(-1.05,1.05)
            ax.set_xlim(a.sweep_pts[0]-0.1,a.sweep_pts[-1]+0.1)
            ax.axhspan(0,1,fill=False,ls='dotted')
            ax.axhspan(-1,0,fill=False,ls='dotted')
        else: 
            a.plot_results_vs_sweepparam(ax= ax,  markersize = 4, save=False, fmt = 'o')
            ax.set_ylim(-1.05,1.05)

        if ii==0:
            p0_sum     = a.p0
            u_p0_sum   = a.u_p0**2 
        else:
            p0_sum     = p0_sum + a.p0
            u_p0_sum   = u_p0_sum + a.u_p0**2
    
    a.p0   = p0_sum/len(timestamp_list_pos)
    a.u_p0 = (u_p0_sum**0.5) / len(timestamp_list_pos) 
    
    a.p0   = a.p0.reshape(-1)[:]
    a.u_p0 = a.u_p0.reshape(-1)[:] 
    return a, folder

def get_data_timestamps(older_than, nr_of_repetitions, carbon = 'C1'):

    ### Initialize data lists
    data_types = [carbon+'_noInit', carbon+'_down', carbon+'_up',
                  '_down_'+carbon+'_neg', '_down_'+carbon+'_pos', '_up_'+carbon+'_neg', '_up_'+carbon+'_pos']
    timestamps = {}
    folders    = {}

    for kk in range(len(data_types)):
        temp_time   = [0]*nr_of_repetitions
        temp_folder = [0]*nr_of_repetitions
        temp_older_than = older_than

        for ii in range(nr_of_repetitions):     
            temp_time[ii], temp_folder[ii] = toolbox.latest_data(contains = data_types[kk], older_than = temp_older_than, return_timestamp = True)
            temp_older_than = temp_time[ii]

        if data_types[kk][0:5] == '_down':    
            timestamps[data_types[kk][1:5]+data_types[kk][8:12]]  = temp_time  
            folders[data_types[kk][1:5]+data_types[kk][8:12]]     = temp_folder
        elif data_types[kk][0:3] == '_up':    
            timestamps[data_types[kk][1:3]+data_types[kk][6:10]]  = temp_time  
            folders[data_types[kk][1:3]+data_types[kk][6:10]]     = temp_folder
        else:    
            timestamps[data_types[kk][3:]] = temp_time  
            folders[data_types[kk][3:]]    = temp_folder
        
    return timestamps, folders


### the fit function for the Ramsey fit
def fit_ramsey_gaussian_decay(g_tau, g_a, *arg):
    """
    fitfunction for a ramsey modulation, with gaussian decay,
        y(x) = a + A*exp(-(x/tau)**2) * mod,

        where:
        mod = sum_i(cos(2pi*f_i*x +phi) - 1)

    Initial guesses (in this order):
        g_tau : decay const
        g_A : Amplitude
        g_a : offset

        For the modulation:
        an arbitrary no of tuples, in the form
        (g_f, g_A)[i] = (frequency, Amplitude, phase)[i]
    """
    fitfunc_str = 'y(x) = a + exp(-(x/tau)**2)*('
    no_frqs = len(arg)
    if no_frqs == 0:
        print 'no modulation frqs supplied'
        return False
    
    tau = fit.Parameter(g_tau, 'tau')
    # A = fit.Parameter(g_A, 'A')
    a = fit.Parameter(g_a, 'a')
    p0 = [tau, a]

    print 'fitting with %d modulation frequencies' % no_frqs

    frqs = []
    amplitudes = []
    phases = []
    print arg
    for i, m in enumerate(arg):
        fitfunc_str += 'A%d*cos(2pi*f%d*x+phi%d)' % (i, i, i)
        frqs.append(fit.Parameter(m[0], 'f%d'%i))
        phases.append(fit.Parameter(m[2], 'phi%d'%i))
        amplitudes.append(fit.Parameter(m[1], 'A%d'%i))
        p0.append(frqs[i])
        p0.append(amplitudes[i])
        p0.append(phases[i])
    fitfunc_str += ')'

    def fitfunc(x):
        prd = exp(-(x/tau())**2)
        mod = 0
        for i in range(no_frqs):
            mod += amplitudes[i]() * (cos(2*pi*frqs[i]()*x+phases[i]()))
        return a() + prd*mod

    return p0, fitfunc, fitfunc_str

### the fit function for the initialization fit
def fit_initialization_fidelity(g_F1, g_A1, g_F2,  g_A2, g_f, g_a, g_A, g_t):
    '''Fit function for an electron Ramsey with/without C13 initialization
    g_F1 -  Fidelity of the strongly coupled C13
    g_A1 -  Hyperfine of the strongly coupled C13
    g_F2 -  Fidelity of the initialized C13
    g_A2 -  Hyperfine of the initialized C13
    g_f  -  Detuning (carrier frequency)
    g_a  -  Offset, maybe fix to 0.5
    g_A  -  Amplitude maybe fix to 0.5
    g_t  -  Decay of Ramsey
    
    The function should take the complete data set (3 measurements) at once and fit it
    '''
 
    fitfunc_str = '''a + A * exp(-(x/t)^2) * [ 
                      F1*F2         *cos[2pi*(f + (A1+A2)/2 )*x] 
                    + F1*(1-F2)     *cos[2pi*(f + (A1-A2)/2 )*x] 
                    + (1-F1)*F2     *cos[2pi*(f + (-A1+A2)/2 )*x] 
                    + (1-F1)*(1-F2) *cos[2pi*(f + (-A1-A2)/2 )*x] 
                    ]'''

    F1  = fit.Parameter(g_F1, 'F1')
    A1  = fit.Parameter(g_A1, 'A1')
    F2  = fit.Parameter(g_F2, 'F2')
    A2  = fit.Parameter(g_A2, 'A2')

    f   = fit.Parameter(g_f, 'f')
    a   = fit.Parameter(g_a, 'a')
    A   = fit.Parameter(g_A, 'A')
    t   = fit.Parameter(g_t, 't')

    p0 = [F1, A1, F2, A2, f, a, A, t]

    def fitfunc(x):
        return (a() + A()*np.exp(-(x/t())**2) * (
                          F1()*F2()         *np.cos(2*np.pi*(f() + (A1()+A2())/2)*x) +
                          F1()*(1-F2())     *np.cos(2*np.pi*(f() + (A1()-A2())/2)*x) +
                          (1-F1())*F2()     *np.cos(2*np.pi*(f() + (-A1()+A2())/2)*x) +
                          (1-F1())*(1-F2()) *np.cos(2*np.pi*(f() + (-A1()-A2())/2)*x))
                          )
    return p0, fitfunc, fitfunc_str

def fit_initialization_fidelity_all(g_F1, g_A1, g_F2,  g_A2, g_f, g_a, g_A, g_t):
    '''Fit function for an electron Ramsey with/without C13 initialization
    g_F1 -  Fidelity of the strongly coupled C13
    g_A1 -  Hyperfine of the strongly coupled C13
    g_F2 -  Fidelity of the initialized C13
    g_A2 -  Hyperfine of the initialized C13
    g_f  -  Detuning (carrier frequency)
    g_a  -  Offset, maybe fix to 0.5
    g_A  -  Amplitude maybe fix to 0.5
    g_t  -  Decay of Ramsey
    
    The function should take the complete data set (3 measurements) at once and fit it
    '''
 
    fitfunc_str = '''a + A * exp(-(x/t)^2) * [ 
                      F1*F2         *cos[2pi*(f + (A1+A2)/2 )*x] 
                    + F1*(1-F2)     *cos[2pi*(f + (A1-A2)/2 )*x] 
                    + (1-F1)*F2     *cos[2pi*(f + (-A1+A2)/2 )*x] 
                    + (1-F1)*(1-F2) *cos[2pi*(f + (-A1-A2)/2 )*x] 
                    ]'''

    F1  = fit.Parameter(g_F1, 'F1')
    A1  = fit.Parameter(g_A1, 'A1')
    F2  = fit.Parameter(g_F2, 'F2')
    A2  = fit.Parameter(g_A2, 'A2')

    f   = fit.Parameter(g_f, 'f')
    a   = fit.Parameter(g_a, 'a')
    A   = fit.Parameter(g_A, 'A')
    t   = fit.Parameter(g_t, 't')

    p0 = [F1, A1, F2, A2, f, a, A, t]

    def fitfunc(x):

        L = len(x_all)/3
               

        x_no_init   = x[0:L]
        x_up        = x[L:2*L]
        x_down      = x[2*L:3*L]


        S_no_init =       (a() + A()*np.exp(-(x_no_init/t())**2) * (
                          0.5*F1()          *np.cos(2*np.pi*(f() + (A1()+A2())/2)*x_no_init) +
                          0.5*F1()          *np.cos(2*np.pi*(f() + (A1()-A2())/2)*x_no_init) +
                          0.5*(1-F1())      *np.cos(2*np.pi*(f() + (-A1()+A2())/2)*x_no_init) +
                          0.5*(1-F1())      *np.cos(2*np.pi*(f() + (-A1()-A2())/2)*x_no_init))
                          )

        S_up =       (a() + A()*np.exp(-(x_up/t())**2) * (
                          F1()*F2()         *np.cos(2*np.pi*(f() + (A1()+A2())/2)*x_up) +
                          F1()*(1-F2())     *np.cos(2*np.pi*(f() + (A1()-A2())/2)*x_up) +
                          (1-F1())*F2()     *np.cos(2*np.pi*(f() + (-A1()+A2())/2)*x_up) +
                          (1-F1())*(1-F2()) *np.cos(2*np.pi*(f() + (-A1()-A2())/2)*x_up))
                          )

        S_down =       (a() + A()*np.exp(-(x_down/t())**2) * (
                          F1()*F2()         *np.cos(2*np.pi*(f() + (A1()-A2())/2)*x_down) +
                          F1()*(1-F2())     *np.cos(2*np.pi*(f() + (A1()+A2())/2)*x_down) +
                          (1-F1())*F2()     *np.cos(2*np.pi*(f() + (-A1()-A2())/2)*x_down) +
                          (1-F1())*(1-F2()) *np.cos(2*np.pi*(f() + (-A1()+A2())/2)*x_down))
                          )

        S_tot = r_[S_no_init, S_up, S_down]
        # S_tot = r_[S_no_init, S_no_init, S_no_init]

        return S_tot

    return p0, fitfunc, fitfunc_str


### get the data locations
''' Data set 1: older than 20141202_092002, 10 measurements, C1, C2, C5
    Data set 2: older than 20141203_212603, 20 measurements, C2'''


timestamp_dict, folders_dict = get_data_timestamps('20141202_092002', 10, carbon = 'C1')
# timestamp_dict, folders_dict = get_data_timestamps('20141203_212603', 20, carbon = 'C2')


'''####################
### Nuclear RO data ###
####################'''
'''
### Get the data
a_C13_RO_up, folder_up = get_and_plot_data_nuc_RO(timestamp_dict['up_pos'],timestamp_dict['up_neg'],ssro_calib_folder)
a_C13_RO_down, folder_down = get_and_plot_data_nuc_RO(timestamp_dict['down_pos'],timestamp_dict['down_neg'],ssro_calib_folder)

### plot for up initialization 
fig,ax = plt.subplots(figsize=(5,5)) 
rects = ax.bar(a_C13_RO_up.sweep_pts,a_C13_RO_up.p0,yerr=a_C13_RO_up.u_p0,align ='center',ecolor = 'k' )
ax.set_xticks(a_C13_RO_up.sweep_pts)
ax.set_xticklabels(a_C13_RO_up.x)
ax.set_ylim(-1.1,1.1)
ax.set_title('Up initialization integrated'+'---'+ str(folder_up))
ax.hlines([-1,0,1],-0.1,2.1,linestyles='dotted')
for ii,rect in enumerate(rects):
    height = rect.get_height()
    plt.text(rect.get_x()+rect.get_width()/2., 1.02*height, str(round(a_C13_RO_up.p0[ii],2)) +'('+ str(int(round(a_C13_RO_up.u_p0[ii]*100))) +')',
        ha='center', va='bottom')
fig.savefig(os.path.join(folder_up,'tomo.png'))

### plot for down initialization 
fig,ax = plt.subplots(figsize=(5,5)) 
rects = ax.bar(a_C13_RO_down.sweep_pts,a_C13_RO_down.p0,yerr=a_C13_RO_down.u_p0,align ='center',ecolor = 'k' )
ax.set_xticks(a_C13_RO_down.sweep_pts)
ax.set_xticklabels(a_C13_RO_down.x)
ax.set_ylim(-1.1,1.1)
ax.set_title('down initialization integrated'+'---'+ str(folder_down))
ax.hlines([-1,0,1],-0.1,2.1,linestyles='dotted')
for ii,rect in enumerate(rects):
    height = rect.get_height()
    plt.text(rect.get_x()+rect.get_width()/2., 1.02*height, str(round(a_C13_RO_down.p0[ii],2)) +'('+ str(int(round(a_C13_RO_down.u_p0[ii]*100))) +')',
        ha='center', va='bottom')
fig.savefig(os.path.join(folder_down,'tomo.png'))

### Final initialization results
average_initialization  = (a_C13_RO_up.p0[2] - a_C13_RO_down.p0[2])/2
average_initialization_u= ((a_C13_RO_up.u_p0[2]**2 + a_C13_RO_down.u_p0[2]**2)**0.5)/2

print 'Initialization by nuclear RO'
print 'Up = '   + str(round(a_C13_RO_up.p0[2],3)) + '+/-' + str(round(a_C13_RO_up.u_p0[2],3))
print 'Down = ' + str(round(a_C13_RO_down.p0[2],3)) + '+/-' + str(round(a_C13_RO_down.u_p0[2],3))
print 'Average = ' + str(round(average_initialization,3)) + '+/-' + str(round(average_initialization_u,3))
'''

'''#########################
### Electron Ramsey data ###
#########################'''
if 0:
    ### load electron ramsey data (and plot individual plots)
    a_noinit, folder = get_and_plot_data(timestamp_dict['noInit'], ssro_calib_folder)
    a_up, folder     = get_and_plot_data(timestamp_dict['up'], ssro_calib_folder)
    a_down, folder   = get_and_plot_data(timestamp_dict['down'], ssro_calib_folder)

    ### Plot the data all together
    fig = a_up.default_fig(figsize=(10,5))
    ax  = a_up.default_ax(fig)
    ax.set_xlim(a_up.x[0]-1,a_up.x[-1]+1)

    ax.errorbar(a_noinit.x,    a_noinit.p0, a_noinit.u_p0,0*np.ones(len(a_noinit.u_p0)), '.b', markersize = 2, label = 'no_init') 
    ax.errorbar(a_up.x,        a_up.p0,     a_up.u_p0,    0*np.ones(len(a_up.u_p0)),     '.r', markersize = 2, label = 'up') 
    ax.errorbar(a_down.x,      a_down.p0,   a_down.u_p0,  0*np.ones(len(a_down.u_p0)),   '.k', markersize = 2, label = 'down') 
    ax.legend()

    ### Fitting the data seperately to Ramsey decays
    guess_f1    = 0.6e-3 #in GHz
    guess_A1    = 0.5
    guess_phi1  = 0.
    guess_f2    = 0.40e-3 #in GHz
    guess_A2    = 0.5
    guess_phi2  = 0.
    guess_tau   = 4600
    guess_a     = 0.5

    fit_result1 = fit.fit1d(a_noinit.x, a_noinit.p0, fit_ramsey_gaussian_decay,
            guess_tau, guess_a, (guess_f1, guess_A1, guess_phi1),
            (guess_f2, guess_A2, guess_phi2),
             fixed=[1,4,7],
            do_print=False, ret=True)
    fit_result2 = fit.fit1d(a_up.x, a_up.p0, fit_ramsey_gaussian_decay,
            guess_tau, guess_a, (guess_f1, guess_A1, guess_phi1),
            (guess_f2, guess_A2, guess_phi2),
             fixed=[1,4,7],
            do_print=False, ret=True)
    fit_result3 = fit.fit1d(a_down.x, a_down.p0, fit_ramsey_gaussian_decay,
            guess_tau, guess_a, (guess_f1, guess_A1, guess_phi1),
            (guess_f2, guess_A2, guess_phi2),
             fixed=[1,4,7],
            do_print=False, ret=True)

    plot.plot_fit1d(fit_result1, np.linspace(0,a_noinit.x[-1],201), ax=ax,
            plot_data=False, linestyle = '-b')
    plot.plot_fit1d(fit_result2, np.linspace(0,a_noinit.x[-1],201), ax=ax,
            plot_data=False, linestyle = '-r')
    plot.plot_fit1d(fit_result3, np.linspace(0,a_noinit.x[-1],201), ax=ax,
            plot_data=False, linestyle = '-k')

    plt.savefig(os.path.join(folder, 'electronramsey_analysis.pdf'),
            format='pdf')
    plt.savefig(os.path.join(folder, 'electronramsey_analysis.png'),
            format='png')

### Fitting the data at once to the initialization fidelities
    ### Plot the data all together
if 0:
    fig = a_up.default_fig(figsize=(10,5))
    ax  = a_up.default_ax(fig)
    ax.set_xlim(a_up.x[0]-1,a_up.x[-1]+1)

    ax.errorbar(a_noinit.x,    a_noinit.p0, a_noinit.u_p0,0*np.ones(len(a_noinit.u_p0)), '.b', markersize = 2, label = 'no_init') 
    ax.errorbar(a_up.x,        a_up.p0,     a_up.u_p0,    0*np.ones(len(a_up.u_p0)),     '.r', markersize = 2, label = 'up') 
    ax.errorbar(a_down.x,      a_down.p0,   a_down.u_p0,  0*np.ones(len(a_down.u_p0)),   '.k', markersize = 2, label = 'down') 
    ax.legend()

    #Frequencies in kHz
    guess_F1    =  0.5
    guess_A1    =  0.180e-3
    guess_F2    =  0.5
    guess_A2    =  1e-6

    guess_f     = 0.5e-3 
    guess_a     = 0.5
    guess_A     = 0.5
    guess_tau   = 4600


    fit_result1 = fit.fit1d(a_noinit.x, a_noinit.p0, fit_initialization_fidelity,
            guess_F1, guess_A1, guess_F2, guess_A2,
            guess_f, guess_a, guess_A,guess_tau,
             fixed=[2,3,5],
            do_print=True, ret=True)
    fit_result2 = fit.fit1d(a_up.x, a_up.p0, fit_initialization_fidelity,
            guess_F1, guess_A1, guess_F2, guess_A2,
            guess_f, guess_a, guess_A,guess_tau,
             fixed=[2,3,5],
            do_print=True, ret=True)
    fit_result3 = fit.fit1d(a_down.x, a_down.p0, fit_initialization_fidelity,
            guess_F1, guess_A1, guess_F2, guess_A2,
            guess_f, guess_a, guess_A,guess_tau,
             fixed=[2,3,5],
            do_print=True, ret=True)

    plot.plot_fit1d(fit_result1, np.linspace(0,a_noinit.x[-1],201), ax=ax,
            plot_data=False, linestyle = '-b')
    plot.plot_fit1d(fit_result2, np.linspace(0,a_noinit.x[-1],201), ax=ax,
            plot_data=False, linestyle = '-r')
    plot.plot_fit1d(fit_result3, np.linspace(0,a_noinit.x[-1],201), ax=ax,
            plot_data=False, linestyle = '-k')

###########################
### to fit all at once: ###
###########################

if 1:
    fig = a_up.default_fig(figsize=(10,5))
    ax  = a_up.default_ax(fig)
    ax.set_xlim(a_up.x[0]-1,a_up.x[-1]+1)

    ax.errorbar(a_noinit.x,    a_noinit.p0, a_noinit.u_p0,0*np.ones(len(a_noinit.u_p0)), '.b', markersize = 2, label = 'no_init') 
    ax.errorbar(a_up.x,        a_up.p0,     a_up.u_p0,    0*np.ones(len(a_up.u_p0)),     '.r', markersize = 2, label = 'up') 
    ax.errorbar(a_down.x,      a_down.p0,   a_down.u_p0,  0*np.ones(len(a_down.u_p0)),   '.k', markersize = 2, label = 'down') 
    ax.legend()

    x_all       =  r_[ a_noinit.x, a_up.x, a_down.x]
    y_all       =  r_[ a_noinit.p0, a_up.p0, a_down.p0]
    y_all_error =  r_[ a_noinit.u_p0, a_up.u_p0, a_down.u_p0] 

    # ax.errorbar(x_all, y_all, y_all_error, 0*np.ones(len(y_all)),'.b', markersize = 2, label = 'no_init')

    #Frequencies in kHz
    guess_F1    =  0.387993
    guess_A1    =  0.181e-3
    guess_F2    =  0
    guess_A2    =  0.020e-3

    guess_f     = 0.522e-3 
    guess_a     = 0.5
    guess_A     = 0.5
    guess_tau   = 4800


    p0, fitfunc, fitfunc_str = fit_initialization_fidelity_all(guess_F1, guess_A1, guess_F2, guess_A2,guess_f, guess_a, guess_A, guess_tau)

    fit_result1 = fit.fit1d(x_all, y_all, fit_initialization_fidelity_all,
            guess_F1, guess_A1, guess_F2, guess_A2,
            guess_f, guess_a, guess_A, guess_tau,
             fixed=[],
            do_print=True, ret=True)

    ### show guess
    L = len(x_all)/3
    guess_curves_no_init =  fitfunc(x_all)[0:L]
    guess_curves_up      =  fitfunc(x_all)[L:2*L]
    guess_curves_down    =  fitfunc(x_all)[2*L:3*L]

    ax.plot( a_noinit.x, guess_curves_no_init, ':r', lw=2)



    # plot.plot_fit1d(fit_result1, x_all, ax=ax,
    #         plot_data=False, linestyle = '-b')
