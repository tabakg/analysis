#Simulates the response of a single carbon atom to a number of decoupling pulses
#Script by MAR
import numpy as np
import matplotlib.pyplot as plt
import h5py
import analysis.lib.qec.nuclear_spin_characterisation as SC
reload(SC)

################
#input arguments ##
################

def main(labpc = True):


    ##############
    ## exp params ##
    ##############
    N = 16
    tau=np.linspace(0e-6, 15e-6, 15000) #seconds

    N_swp = np.array(range(0,400,2)) #Integer
    # tau_swpN= 6.522e-6 #seconds
    tau_swpN = 6.62e-6
    # tau_swpN = 12.08e-6 #8.840e-6
    B_Field = 304.12 #Gauss
    pulseF = .86 #correction factor on final signal for plotting (pulse fidelity )

    ########
    # Reproduce fit of other analysis script
    ########
    f = 0.274053
    a = 0.5437
    A = 0.4377

    n = np.linspace(0,40,10000)
    cos_fit = a + A* np.cos(2*np.pi*f*n)


    ####################
    ## Hyperfine strenghts ##
    # ####################

    # HF_par = [30e3, 27e3,-62.5e3]
    # HF_orth =[80e3,30e3,130e3]

    # HF_par = [30e3, 27e3,-62.5e3]
    # HF_orth =[80e3,28.5e3,130e3]

    HF_par = [30e3, 27e3,-62.5e3]
    HF_orth =[80e3,28.5e3,132e3]

    Mn = SC.dyn_dec_signal(HF_par,HF_orth,B_Field,N_swp,tau_swpN)
    sweep_N_comb_signal = ((Mn.prod(axis=0) +1)/2)
    sweep_N_signal = ((Mn+1)/2)

    Mt = SC.dyn_dec_signal(HF_par,HF_orth,B_Field,N,tau)
    FP_comb_signal  = ((Mt.prod(axis=0) +1)/2)
    FP_signal = ((Mt+1)/2)


    #########################
    ##### Importing data #######
    #########################
    if labpc == True:
        pass
        #Script that uses toolbox functions
    else:
        filepaths = []
        datestamp = '20140410'
        timestamps = ['165509']
        # datestamp = '20140408'
        # timestamps = ['174302'] #tau = 6.622 ,spin 2
        # timestamps = ['164854','165446'] #tau = 6.522us , testspin 1

        datadir = '/Users/Adriaan/Documents/teamdiamond/data/'
        filepath = datadir+'/'+datestamp+'/TIMESTAMP_DecouplingSequence_Hans_sil1_C3_sweep_N/TIMESTAMP_DecouplingSequence_Hans_sil1_C3_sweep_N.hdf5'

        for i, timestamp in enumerate(timestamps):
            filepaths.append(filepath.replace("TIMESTAMP",timestamp))

        data_N= []
        signal_swp_N = []
        for filep in filepaths:
            d_N, sig =  load_dd_fingerprintdata(filep)
            data_N.extend(d_N)
            signal_swp_N.extend(sig)

        filepaths = []
        if N ==16:
            filepath = datadir+'/fingerprint_data/TIMESTAMP_DecouplingSequence_Fingerprint_Hans_sil1_N1024/TIMESTAMP_DecouplingSequence_Fingerprint_Hans_sil1_N1024.hdf5'
            timestamps = ['223450', '223801', '224119', '224446', '231158','225215', '225614', '230023', '231645', '232118', '232603', '233057', '233605', '234654', '111324', '111725', '112126', '112529', '112930', '113614', '114015', '114416', '114818', '115220', '115622', '120024', '120426','120825']#, '130753']
        elif N ==32:
            filepath = '/Users/Adriaan/Documents/Python_Programs/Data/fingerprint_data/TIMESTAMP_DecouplingSequence_Hans_sil1_N32/TIMESTAMP_DecouplingSequence_Hans_sil1_N32.hdf5'
            timestamps =['101732','102646','104011',
'105345']


        for i, timestamp in enumerate(timestamps):
            filepaths.append(filepath.replace("TIMESTAMP",timestamp))
        data_tau= []
        signal_tau = []
        for filep in filepaths:
            d_tau, sig =  load_dd_fingerprintdata(filep)
            data_tau.extend(d_tau)
            signal_tau.extend(sig)


    ##########
    #Plotting
    ##########
    plt.figure()
    plt.xlabel('N')
    plt.ylabel('Signal_swp_N')

    plt.plot(N_swp,sweep_N_signal[0,:]*pulseF,'r.-',label='test_spin1')
    plt.plot(N_swp,sweep_N_signal[1,:]*pulseF,'c.-',label='test_spin2')
    plt.plot(N_swp,sweep_N_signal[2,:]*pulseF,'g.-',label='test_spin3')
    plt.plot(N_swp,sweep_N_comb_signal*pulseF,'k--',label ='Combined signal of test spins',linewidth=1.5)
    # plt.plot(data_N,signal_swp_N,'b.-',linewidth = 0.5,label='measured_data')
    # plt.plot(n,cos_fit,'r-',linewidth = 0.5,label='cos fit of data')
    plt.legend(loc=4)
    plt.grid()

    plt.figure()
    plt.xlabel('tau')
    plt.ylabel('Signal')

    plt.xlabel('tau')
    plt.ylabel('Signal')
    plt.plot(tau*1e6,FP_signal[0,:]*pulseF,'r-',label='test_spin1')
    plt.plot(tau*1e6,FP_signal[1,:]*pulseF,'c-',label='test_spin2')
    plt.plot(tau*1e6,FP_signal[2,:]*pulseF,'g-',label='test_spin3')
    plt.plot(tau*1e6,FP_comb_signal*pulseF,'k--',label ='Combined signal of test spins',linewidth=1.5)
    plt.xlim(0,15)
    plt.grid()

    plt.plot(data_tau,signal_tau,'b.-',linewidth = 0.5,label='measured_data')
    plt.legend(loc=4)
    plt.show()



def load_dd_fingerprintdata(h5filepath):
    '''
    Loads fingerprint data when not on a lab pc
    '''
    f = h5py.File(h5filepath,'r')
    name = f.keys()[0]
    g = f[name]
    adwingrpname = g.keys()[0]
    adwingrp = g[adwingrpname]
    sweep_length = adwingrp.attrs['sweep_length']
    reps_per_ROsequence = adwingrp.attrs['reps_per_ROsequence']

    ssro_results = np.reshape((adwingrp['ssro_results'].value),(reps_per_ROsequence,sweep_length))
    sweep_pts = adwingrp.attrs['sweep_pts'] #in us
    RO_data = np.sum(ssro_results,axis=0)/float(reps_per_ROsequence)

    xdata = sweep_pts
    ydata = RO_data
    return xdata,ydata

main()
# estimate_HFs()
# load_dd_fingerprintdata()
