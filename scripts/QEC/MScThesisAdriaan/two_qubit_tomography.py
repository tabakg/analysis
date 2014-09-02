import numpy as np
import os
from analysis.lib.tools import toolbox
from analysis.lib.m2.ssro import mbi
from analysis.lib.QEC import conditionalparity as CP
reload (CP)
from matplotlib import pyplot as plt

def BarPlotTomo(timestamp = None, measurement_name = ['adwindata'],folder_name ='Tomo',
        post_select = False,
        ssro_calib_timestamp =None, save = True, plot_fit = True,
        guess = None,
        figsize = (3,2), linewidth = 2, markersize = 2, fontsize =10,xticks = None,barwidth = .8,
        title =None ,savename ='Tomo'):

    '''
    Function that makes a bar plot with errorbars of MBI type data
    '''
    plt.rc('font', size=fontsize)
    if timestamp == None:
        timestamp, folder   = toolbox.latest_data(folder_name,return_timestamp =True)
        print 'Data folder found: %s' %(timestamp)
    else:
        folder = toolbox.data_from_time(timestamp)

    if ssro_calib_timestamp == None:
        ssro_timestamp, ssro_calib_folder = toolbox.latest_data('SSRO', older_than = timestamp, return_timestamp = True)
        print 'SSRO folder found: %s' %(ssro_timestamp)
    else:
        ssro_dstmp, ssro_tstmp = toolbox.verify_timestamp(ssro_calib_timestamp)
        ssro_calib_folder = toolbox.datadir + '/'+ssro_dstmp+'/'+ssro_tstmp+'_AdwinSSRO_SSROCalibration_Hans_sil1'

    a = CP.ConditionalParityAnalysis(folder)
    a.get_sweep_pts()
    a.get_readout_results(name='adwindata', post_select = post_select)

    a.get_electron_ROC(ssro_calib_folder)

    x_labels = a.sweep_pts.reshape(-1)

    if post_select == False:
        y,y_err = a.convert_fidelity_to_contrast(a.p0,a.u_p0)

        print 'Y as calculated by function'
        print y
        x = range(len(y))

        y_a= ((a.p0.reshape(-1)[:])-0.5)*2
        print 'Y as calculated by hand'
        print y_a
        print 'difference'
        print y-y_a

        y_err_a = 2*a.u_p0.reshape(-1)[:]



        if plot_fit ==True:
            fig,ax = plt.subplots()
            ax.bar(x,y,yerr=y_err,align ='center',ecolor = 'k' )
            ax.set_xticks(x)
            if title == None:
                ax.set_title(str(folder)+'/'+str(timestamp))
            else:
                ax.set_title(title)
            print x_labels
            ax.set_xticklabels(x_labels.tolist())
            ax.set_ylim(-1,1)
            ax.hlines([-1,0,1],x[0]-1,x[-1]+1,linestyles='dotted')

        if save and ax != None:
            try:
                fig.savefig(os.path.join(folder, savename+'.pdf'),
                        format='pdf',bbox_inches='tight')

            except:
                print 'Figure has not been saved.'
    else: #if post_select == True:
        c0_0,u_c0_0 =  a.convert_fidelity_to_contrast(a.p0_0,a.u_p0_0)
        c0_1,u_c0_1 =  a.convert_fidelity_to_contrast(a.p0_1,a.u_p0_1)

        x = range(len(c0_0))

        if plot_fit == True:
            fig_0,ax_0 = plt.subplots()
            ax_0.bar(x,c0_0,yerr=u_c0_0,align ='center',ecolor = 'k' )
            # ax_0.bar(x,a.p0_0,yerr = u_c0_0,align = 'center',ecolor = 'k')
            ax_0.set_xticks(x)
            if title == None:
                ax_0.set_title(str(folder)+'/'+str(timestamp)+'0')
            else:
                ax_0.set_title(str(title)+'0')

            ax_0.set_xticklabels(x_labels.tolist())
            # ax_0.set_ylim(-1,1)
            ax_0.hlines([-1,0,1],x[0]-1,x[-1]+1,linestyles='dotted')

            fig_1,ax_1 = plt.subplots()
            ax_1.bar(x,c0_1,yerr=u_c0_1,align ='center',ecolor = 'k' )
            ax_1.set_xticks(x)
            if title == None:
                ax_1.set_title(str(folder)+'/'+str(timestamp)+'1')
            else:
                ax_1.set_title(str(title)+'1')
            ax_1.set_xticklabels(x_labels.tolist())
            # ax_1.set_ylim(-1,1)
            ax_1.hlines([-1,0,1],x[0]-1,x[-1]+1,linestyles='dotted')

            if save and ax_1 != None and ax_0!=None:
                try:
                    fig_0.savefig(os.path.join(folder, str(title)+'0.pdf'),
                            format='pdf',bbox_inches='tight')

                    fig_1.savefig(os.path.join(folder, str(title)+'1.pdf'),
                            format='pdf',bbox_inches='tight')

                except:
                    print 'Figure has not been saved.'

def BarPlotTomoContrast(timestamps=None, measurement_name = ['adwindata'],folder_name ='Tomo',
        ssro_calib_timestamp =None, save = True,
        plot_fit = True, guess = None, mirror_data_points = None,
        figsize = (3,2), linewidth = .4, markersize = 2, fontsize =10, barwidth = 0.8,
        title =None ,savename ='Tomo_pos_neg'):
    '''
    Function that makes a bar plot with errorbars of MBI type data that has been measured with a positive
    and negative RO.

    '''
    plt.rc('font', size=fontsize)
    ### SSRO calibration
    if ssro_calib_timestamp == None:
        ssro_calib_folder = toolbox.latest_data('SSRO', older_than =timestamps[0])
    else:
        ssro_dstmp, ssro_tstmp = toolbox.verify_timestamp(ssro_calib_timestamp)
        ssro_calib_folder = toolbox.datadir + '/'+ssro_dstmp+'/'+ssro_tstmp+'_AdwinSSRO_SSROCalibration_Hans_sil1'

    ### Obtain and analyze data

    folder_a = toolbox.data_from_time(timestamps[0])
    a = mbi.MBIAnalysis(folder_a)
    a.get_sweep_pts()
    a.get_readout_results(name='adwindata')
    a.get_electron_ROC(ssro_calib_folder)
    y_a= ((a.p0.reshape(-1)[:])-0.5)*2
    y_err_a = 2*a.u_p0.reshape(-1)[:]
    if np.size(timestamps) != 1:

        folder_b = toolbox.data_from_time(timestamps[1])
        b = mbi.MBIAnalysis(folder_b)
        b.get_sweep_pts()
        b.get_readout_results(name='adwindata')
        b.get_electron_ROC(ssro_calib_folder)
        y_b= ((b.p0.reshape(-1)[:])-0.5)*2
        y_err_b = 2*b.u_p0.reshape(-1)[:]
        ### Combine data
        y = (y_a - y_b)/2.
        y_err =  1./2*(y_err_a**2 + y_err_b**2)**0.5
        # print y
    else:
        y = y_a
        y_err = y_err_a

    x_labels = a.sweep_pts.reshape(-1)[:]
    x = range(len(y_a))


    if mirror_data_points != None:
        for x_repl in mirror_data_points:
            y[x_repl] = -y[x_repl]

    fig,ax = plt.subplots(figsize=figsize)
    if guess != None:
        x_g =guess[0]
        y_g = guess[1]
        ax.bar(x_g,y_g, color = '0.75' , align = 'center' ,width = (barwidth*1.1),linewidth = 0)
        F_ent   = (1 + y[x_g[0]]*y_g[0] +y[x_g[1]]*y_g[1] +y[x_g[2]]*y_g[2])/4
        u_F_ent = ( y_err[x_g[0]]**2 + y_err[x_g[1]]**2+ y_err[x_g[2]]**2)**.5/4
        print 'Fidelity to guess = %s +/- %s' %(F_ent,u_F_ent)


    if plot_fit ==True:
        ax.bar(x,y,yerr=y_err,align ='center',ecolor = 'k' ,width = barwidth,linewidth = linewidth)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels.tolist(),fontsize = (fontsize-2),rotation = 60)
        ax.set_xlabel(r'Bases', fontsize = fontsize)

        ax.set_ylim(-1.05,1.05)
        ax.yaxis.set_ticks( [-1,-0.5,0,0.5,1])
        ax.set_ylabel(r'Contrast', fontsize = fontsize)
        if title == None:
            title = str(folder_a)
        ax.set_title(title)
        ax.hlines([0],x[0]-0.75,x[-1]+0.75,linewidth = linewidth+0.1) #,linestyles='dotted'



    if save and ax != None:
        print folder_a
        try:
            fig.savefig(os.path.join(folder_a, savename+'.pdf'),
                format='pdf',bbox_inches='tight')
            print' Figure saved in %s' %folder_a
        except:
            print 'Figure has not been saved.'
