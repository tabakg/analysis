
import matplotlib
#mpl.rcParams['text.usetex']=True
#mpl.rcParams['text.latex.unicode']=True
execfile('D:/measuring/analysis/scripts/setup_analysis.py')
from matplotlib import rc, cm
from analysis.lib.magnetometry import adaptive_magnetometry as magnetometry
from analysis.lib.magnetometry import plotting_tools as pt

reload(magnetometry)
reload(pt)
load_data=False


def compare_cappellaro_G3_fid087 ():
    tag = 'simulated_adaptive_magnetometry'
    t_stamps = ['20141215_152517', '20141215_152820', '20141215_153251', '20141215_153913', '20141215_154728', '20141215_155704']
    labels = ['F=0', 'F=1', 'F=2', 'F=3', 'F=4', 'F=5']
    colours = ['k', 'r', 'b', 'g', 'RoyalBlue', 'c']
    pt.compare_multiple_plots (timestamps=t_stamps, labels=labels, title = 'adaptive phase update (G=3) - F0 = 0.87', colours=colours)

def compare_nonadaptive_G3_fid087 ():
    t_stamps = ['20141215_152604', '20141215_152939', '20141215_153454', '20141215_154152', '20141215_155054', '20141215_160056']
    labels = ['F=0', 'F=1', 'F=2', 'F=3', 'F=4', 'F=5']
    colours = ['k', 'r', 'b', 'g', 'RoyalBlue', 'c']
    pt.compare_multiple_plots (timestamps=t_stamps, labels=labels, title = 'non adaptive (G=3) - F0 = 0.87', colours=colours)

def compare_capp_modCapp_supplInfo ():
    t_stamps = ['20150121_134642', '20150113_104934']
    labels = ['adptv phase update', 'modified adptv phase update']
    colours = ['RoyalBlue', 'crimson']
    pt.compare_multiple_plots (timestamps=t_stamps, labels=labels, title = 'G=3, F=0', colours=colours, do_save=True)
    t_stamps = ['20150121_172948', '20150113_164200']
    labels = ['adptv phase update', 'modified adptv phase update']
    colours = ['RoyalBlue', 'crimson']
    pt.compare_multiple_plots (timestamps=t_stamps, labels=labels, title = 'G=3, F=5', colours=colours, do_save=True)


def compare_cappellaro_G2_fid1():
	t_stamps = []
	for i in [0,1,2,3,4,5]:
		t_stamps.append('modCapp_N=10G=2F='+str(i)+'_fid0=1.0')
	labels = ['F=0', 'F=1', 'F=2', 'F=3', 'F=4', 'F=5']
	colours = ['k', 'r', 'b', 'g', 'RoyalBlue', 'c']
	pt.compare_multiple_plots (timestamps=t_stamps, labels=labels, title = 'adaptive (G=2) - F0 = 1', colours=colours)

def return_t_stamps(protocol, N, G, fid, name, F_array=None):
	t_stamps = []
	if not(F_array):
		F_array = [0,1,2, 3, 4, 5]

	for i in F_array:
		t_stamps.append('_'+protocol+'_N='+str(N)+'G='+str(G)+'F='+str(i)+'_fid0='+fid+name)
	return t_stamps	

def compare_protocols_old (pr1, pr2, N, G, fid, name = ''):

	t_stamps = return_t_stamps (protocol = pr1, N=N, G=G, fid=fid, name=name, F_array = [3,4,5])
	dict_G2_adptv = pt.generate_data_dict(timestamps=t_stamps)
	plot_colors =  ['RoyalBlue', 'crimson', 'forestgreen', 'deepskyblue', 'gold','darkslategray', 'cornsilk', 'darkkhaki', 'darkviolet', 'limegreen']
	pt.compare_scalings (data_dict = dict_G2_adptv, title = pr1+' (G='+str(G)+') -- fid0 = '+fid+name, do_save=True, add_HL_plot = False, colours = plot_colors)
	pt.compare_variance_with_overhead (data_dict=dict_G2_adptv, title = pr1+' (G='+str(G)+') -- fid0 = '+fid+name, do_save = True, overhead = 300e-6, colours = plot_colors)
	t_stamps = return_t_stamps (protocol = pr2, N=N, G=G, fid=fid, name=name, F_array = [6,7,8])
	dict_G2_nonadptv = pt.generate_data_dict(timestamps=t_stamps)
	pt.compare_scalings (data_dict = dict_G2_nonadptv, title = pr2+' (G='+str(G)+') -- fid0 = '+name, do_save=True, add_HL_plot = False, colours = plot_colors)
	pt.compare_variance_with_overhead (data_dict=dict_G2_nonadptv, title = pr2+' (G='+str(G)+') -- fid0 = '+fid+name, do_save = True, overhead = 300e-6, colours = plot_colors)
	pt.compare_best_sensitivities ([dict_G2_adptv, dict_G2_nonadptv], title =  'G='+str(G)+' -- fid0 = '+fid+name, legend_array = [pr1, pr2], do_save=True, colours = plot_colors)
	pt.compare_scaling_fits ([dict_G2_adptv, dict_G2_nonadptv], title = 'G='+str(G)+' -- fid0 = '+fid+name, legend_array = [pr1, pr2], do_save=True, colours = plot_colors)

def compare_protocols (protocol_array, N, G, fid, name = ''):

	plot_colors =  ['RoyalBlue', 'crimson', 'forestgreen', 'deepskyblue', 'gold','darkslategray', 'cornsilk', 'darkkhaki', 'darkviolet', 'limegreen']
	dict_array = []

	for j,pr in enumerate(protocol_array):
		t_stamps = return_t_stamps (protocol = pr, N=N, G=G, fid=fid[j], name=name, F_array = [0,1,2,3,4, 5])
		print pr, t_stamps
		dict_gen= pt.generate_data_dict(timestamps=t_stamps)
		dict_array.append(dict_gen)
		pt.compare_scalings (data_dict = dict_gen, title = pr+' (G='+str(G)+') -- fid0 = '+fid[j]+name, do_save=False, add_HL_plot = False, colours = plot_colors)
		pt.compare_variance_with_overhead (data_dict=dict_gen, title = pr1+' (G='+str(G)+') -- fid0 = '+fid[j]+name, do_save = False, overhead = 300e-6, colours = plot_colors)

	sens_dict = pt.compare_best_sensitivities (dict_array, title =  'G='+str(G)+' -- fid0 = '+fid[j]+name, legend_array = protocol_array, do_save=True, colours = plot_colors)
	#pt.compare_scaling_fits (dict_array, title = 'G='+str(G)+' -- fid0 = '+fid[j]+name, legend_array = protocol_array, do_save=True, colours = plot_colors)
	return sens_dict

def compare_room_temperature ():
	pr1 = 'nnAdptv'
	pr2 = 'swarmOpt'
	sens_dict = compare_protocols (protocol_array = [pr1, pr2, pr1, pr2], N=10, G=5, fid=['0.88', '0.88', '1.0', '1.0'], name='_noT2')
	nn88 = sens_dict['0']
	sw88 = sens_dict['1']
	nn100 = sens_dict['2']
	sw100 = sens_dict['3']

	matplotlib.rc ('xtick', labelsize=15)
	matplotlib.rc ('ytick', labelsize=15)
	f1 = plt.figure(figsize = (10,7))
	plt.semilogy (sw88['F'], sw88['sensitivity'], 'RoyalBlue', linewidth =3)
	plt.semilogy (nn88['F'], nn88['sensitivity'],'RoyalBlue', linestyle='--', linewidth =3)
	plt.semilogy (sw88['F'], 3600*sw88['sensitivity'], 'crimson', linewidth =3)
	plt.semilogy (nn88['F'], 3600*nn88['sensitivity'],'crimson', linestyle='--', linewidth =3)
	plt.semilogy (sw100['F'], 50000*sw100['sensitivity'], 'forestgreen', linewidth =3)
	plt.semilogy (nn100['F'], 50000*nn100['sensitivity'],'forestgreen', linestyle='--', linewidth =3)
	plt.ylabel ('minimum sensitivity', fontsize=15)
	plt.xlabel ('F', fontsize=15)
	f1.savefig (r"M:\tnw\ns\qt\Diamond\Projects\Magnetometry with adaptive measurements\Data\analyzed data\compare_sens_roomTemperature.svg")
	f1.savefig (r"M:\tnw\ns\qt\Diamond\Projects\Magnetometry with adaptive measurements\Data\analyzed data\compare_sens_roomTemperature.pdf")
	plt.show()

#compare_capp_modCapp_supplInfo ()
pr1 = 'nnAdptv'
pr2 = 'swarmOpt'
#compare_protocols (pr1=pr1, pr2=pr2, N=10, G=5, fid='1.0', name='_incl_T2')
compare_protocols (protocol_array = [pr1, pr3, pr2], N=10, G=5, fid=['0.88', '0.88', '0.88'], name='_noT2')
#compare_protocols (pr1=pr1, pr2=pr2, N=10, G=3, fid='1.0', name='_incl_T2')
#compare_protocols (pr1=pr1, pr2=pr2, N=10, G=3, fid='0.75', name='_incl_T2')

#compare_protocols (N=10, G=2, fid='0.75')
#compare_protocols (N=10, G=3, fid='0.75')
#compare_protocols (N=10, G=4, fid='0.75')
#compare_protocols (N=10, G=5, fid='0.75')
#compare_protocols (N=10, G=10, fid='0.75')
#compare_protocols (N=10, G=10, fid='1.0')
#compare_protocols (N=10, G=2, fid='0.87')
#compare_protocols (N=10, G=3, fid='0.87')
#compare_protocols (N=10, G=4, fid='0.87')
#compare_protocols (N=10, G=5, fid='0.87')
#compare_protocols (N=10, G=10, fid='0.87')

'''
G=3
t_stamps = ['20141215_152517', '20141215_152820', '20141215_153251', '20141215_153913']
dict_G3_adptv = pt.generate_data_dict(timestamps = t_stamps)
pt.compare_scalings (data_dict = dict_G3_adptv, title = 'Cappellaro (G='+str(G)+') -- fid0 = '+fid+name, do_save=True, add_HL_plot = True)
pt.compare_variance_with_overhead (data_dict=dict_G3_adptv, title = 'Cappellaro (G='+str(G)+') -- fid0 = '+fid+name, do_save = False, overhead = 300e-6)
pt.compare_sensitivity_repRate (data_dict_array = [dict_G3_adptv, dict_G3_adptv], legend_array=['test1', 'test2'], title='test', colours=None, do_save = True, overhead = 200e-6)
'''
#compare_scalings (data_dict_array, title, colours=None)
#compare_cappellaro_G2_fid1()
#compare_cappellaro_G3_fid087()
#compare_nonadaptive_G3_fid087()
#20141215_152517_simulated_adaptive_magnetometry_N=10G=3F=0_fid0=0.87