import numpy as np
import os
from analysis.lib.tools import toolbox
from analysis.lib.m2.ssro import mbi
from matplotlib import pyplot as plt

def BarPlotTomo(timestamp = None, measurement_name = ['adwindata'],folder_name ='Tomo',
		ssro_calib_timestamp =None, save = True,
		plot_fit = True) :
	'''
	Function that makes a bar plot with errorbars of MBI type data 
	'''
	if timestamp == None:
	    timestamp, folder   = toolbox.latest_data(folder_name,return_timestamp =True)
	else: 
	    folder = toolbox.data_from_time(timestamp) 

	if ssro_calib_timestamp == None: 
	    ssro_calib_folder = toolbox.latest_data('SSRO')
	else:
	    ssro_dstmp, ssro_tstmp = toolbox.verify_timestamp(ssro_calib_timestamp)
	    ssro_calib_folder = toolbox.datadir + '/'+ssro_dstmp+'/'+ssro_tstmp+'_AdwinSSRO_SSROCalibration_Hans_sil1'

	a = mbi.MBIAnalysis(folder)
	a.get_sweep_pts()
	a.get_readout_results(name='adwindata')
	a.get_electron_ROC(ssro_calib_folder)

	x_labels = a.sweep_pts.reshape(-1)
	y= ((a.p0.reshape(-1))-0.5)*2
	x = range(len(y)) 
	y_err = 2*a.u_p0.reshape(-1)

	if plot_fit ==True: 
		fig,ax = plt.subplots() 
		rects = ax.bar(x,y,yerr=y_err,align ='center',ecolor = 'k' )
		ax.set_xticks(x)
		# ax.title = timestamp
		print x_labels
		ax.set_xticklabels(x_labels.tolist())
		ax.set_ylim(-1.1,1.1)
		ax.set_title(str(folder)+'/'+str(timestamp))
		# ax.grid()
		ax.hlines([-1,0,1],x[0]-1,x[-1]+1,linestyles='dotted')


			# print values on bar plot
	def autolabel(rects):
	    for ii,rect in enumerate(rects):
	        height = rect.get_height()
	        plt.text(rect.get_x()+rect.get_width()/2., 1.02*height, str(round(y[ii],2)) +'('+ str(int(round(y_err[ii]*100))) +')',
	            ha='center', va='bottom')
	autolabel(rects)

	if save and ax != None:
		try:
		    fig.savefig(
		        os.path.join(folder,'tomo.png'))
		except:
		    print 'Figure has not been saved.'

def BarPlotTomoContrast(timestamps = [None,None], measurement_name = ['adwindata'],folder_name ='Tomo',
		ssro_calib_timestamp =None, save = True,
		plot_fit = True) :
	'''
	Function that makes a bar plot with errorbars of MBI type data that has been measured with a positive
	and negative RO.
	'''

	### SSRO calibration
	if ssro_calib_timestamp == None: 
	    ssro_calib_folder = toolbox.latest_data('SSRO')
	else:
	    ssro_dstmp, ssro_tstmp = toolbox.verify_timestamp(ssro_calib_timestamp)
	    ssro_calib_folder = toolbox.datadir + '/'+ssro_dstmp+'/'+ssro_tstmp+'_AdwinSSRO_SSROCalibration_Hans_sil1'

	### Obtain and analyze data
		### postive RO data
	if timestamps[0] == None: 
		folder_a = toolbox.latest_data(contains='positive')
	else:		
		folder_a = toolbox.data_from_time(timestamps[0])      
	
	a = mbi.MBIAnalysis(folder_a)
	a.get_sweep_pts()
	a.get_readout_results(name='adwindata')
	a.get_electron_ROC(ssro_calib_folder)
	y_a= ((a.p0.reshape(-1)[:])-0.5)*2
	y_err_a = 2*a.u_p0.reshape(-1)[:] 

		### negative RO data
	if timestamps[1] == None: 
		folder_b = toolbox.latest_data(contains='negative')
	else:	
		folder_b = toolbox.data_from_time(timestamps[1])      
 	
	b = mbi.MBIAnalysis(folder_b)
	b.get_sweep_pts()
	b.get_readout_results(name='adwindata')
	b.get_electron_ROC(ssro_calib_folder)
	y_b= ((b.p0.reshape(-1)[:])-0.5)*2
	y_err_b = 2*b.u_p0.reshape(-1)[:] 

	x_labels = a.sweep_pts.reshape(-1)[:]
	x = range(len(y_a)) 


	
	### Combine data
	y = (y_a - y_b)/2.
	y_err =  1./2*(y_err_a**2 + y_err_b**2)**0.5 
	

	print folder_a
	print folder_b

	print y_a
	print y_b
	print y

	### Fidelities
	# F_ZZ 	= (1 + y[2] + y[5] + y[14])/4
	# F_ZmZ 	= (1 + y[2] - y[5] - y[14])/4
	# F_ent 	= (1 + y[0] -y[4] -y[8])/4
	# F_ent 	= (1 + y[0] +y[1] +y[2])/4
	# print 'Fidelity with ZZ  = ' + str(F_ZZ)
	# print 'Fidelity with ZmZ  = ' + str(F_ZmZ)
	# print 'Fidelity with ent = ' + str(F_ent)



	if plot_fit ==True: 
		fig,ax = plt.subplots() 
		rects = ax.bar(x,y,yerr=y_err,align ='center',ecolor = 'k' )
		ax.set_xticks(x)
		ax.set_xticklabels(x_labels.tolist())
		ax.set_ylim(-1.1,1.1)
		ax.set_title(str(folder_a)+'/'+str(timestamps[0]))
		ax.hlines([-1,0,1],x[0]-1,x[-1]+1,linestyles='dotted')

		# print values on bar plot
	def autolabel(rects):
	    for ii,rect in enumerate(rects):
	        height = rect.get_height()
	        plt.text(rect.get_x()+rect.get_width()/2., 1.02*height, str(round(y[ii],2)) +'('+ str(int(round(y_err[ii]*100))) +')',
	            ha='center', va='bottom')
	autolabel(rects)

	if save and ax != None:
		try:
		    fig.savefig(
		        os.path.join(folder_a,'tomo.png'))
		except:
		    print 'Figure has not been saved.'