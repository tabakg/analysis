from analysis.lib.nv import nvlevels
reload(nvlevels)
import numpy as np
from matplotlib import pyplot as plt

def plot_ES_b_dependence(strain_splitting=2.):
	b_range=np.linspace(0,1000,100) #gauss
	Ex=strain_splitting/2. #Ex is approx strain_splitting divided by 2
	spectrum=np.zeros((6,))
	#plt.close()
	for Bz in b_range:
		spectrum=np.vstack((spectrum,np.sort(nvlevels.get_ES(
															E_field=[Ex,0.,0.], 
															B_field=[0.,0.,Bz],
															Ee0=-1.94,
															transitions=False,
															)[0])))
	spectrum=spectrum[1:]

	for i in range(6):
		plt.plot(b_range,spectrum[:,i])
		plt.savefig('D:/jcramer3/My Documents/QEC/nv_levels_sym/ES_B_dependence_Ex_'+str(Ex)+'.png')

def plot_GS_b_dependence(strain_splitting=2.):
	b_range=np.linspace(0,1000,100) #gauss
	Ex=strain_splitting/2. #Ex is approx strain_splitting divided by 2
	spectrum=np.zeros((3,))
	plt.close()
	for Bz in b_range:
		spectrum=np.vstack((spectrum,np.sort(nvlevels.get_GS(
															E_field=[Ex,0.,0.], 
															B_field=[0.,0.,Bz],
															)[0])))
	spectrum=spectrum[1:]

	for i in range(3):
		plt.plot(b_range,spectrum[:,i])
		plt.savefig('D:/jcramer3/My Documents/QEC/nv_levels_sym/GS_B_dependence.png')

def plot_ES_e_dependence(Bz=20.):
	e_range=np.linspace(0,10,100) #gauss
	spectrum=np.zeros((6,))
	# plt.close()
	plt.figure()
	for Ex in e_range:
		spectrum=np.vstack((spectrum,np.sort(nvlevels.get_ES(
															E_field=[Ex,0.,0.], 
															B_field=[0.,0.,Bz],
															Ee0=-1.94,
															transitions=False,
															)[0])))
	spectrum=spectrum[1:]


	for i in range(6):
		plt.plot(e_range,spectrum[:,i])
		plt.title('Excited state levels E dependence, Bz = '+str(Bz))
		plt.xlabel('Strain E (GHz)')
		plt.ylabel('relative energy (GHz)')
		plt.savefig('D:/jcramer3/My Documents/QEC/nv_levels_sym/ES_E_dependence_Bz_'+str(Bz)+'.png')

def plot_transitions_b_dependence(strain_splitting=2.5):
	b_range=np.linspace(300,600,50) #gauss
	Ex=strain_splitting/2. #Ex is approx strain_splitting divided by 2
	no_transitions=18
	spectrum=np.zeros((no_transitions,))
	# plt.close()
	plt.figure()
	for Bz in b_range:
		spectrum=np.vstack((spectrum,nvlevels.get_optical_transitions(show_E_transitions=True,
																show_A_transitions=True,
																show_FB_E_transitions=True, 
                            									show_FB_A_transitions=True, 
                            									show_E_prime_flip_transitions=True,
															E_field=[Ex,0.,0.], 
															B_field=[0,0.,Bz],
															Ee0=-1.94,
															)))
	spectrum=spectrum[1:]

	for i in range(no_transitions):
		plt.title('Transitions B dependence, Ex = '+str(Ex))
		plt.xlabel('Magnetic field Bz (G)')
		plt.ylabel('relative energy difference (GHz)')
		if i < 4:
			style = 2
		else: style =0.5
		plt.plot(b_range,spectrum[:,i],linewidth = style)
		plt.savefig('D:/jcramer3/My Documents/QEC/nv_levels_sym/Transitions_B_dependence_Ex_'+str(Ex)+'.png')

def plot_transitions_bx_dependence(Bz=300,strain_splitting=2.5):
	bx_range=np.linspace(0,500,100) #gauss
	Ex=strain_splitting/2. #Ex is approx strain_splitting divided by 2
	no_transitions=18
	spectrum=np.zeros((no_transitions,))
	plt.close()
	for Bx in bx_range:
		spectrum=np.vstack((spectrum,nvlevels.get_optical_transitions(
															E_field=[Ex,0.,0.], 
															B_field=[Bx,0.,Bz],
															Ee0=-1.94,
															show_FB_E_transitions=True
															)))
	spectrum=spectrum[1:]

	for i in range(no_transitions):

		plt.plot(bx_range,spectrum[:,i])
		plt.savefig('D:/jcramer3/My Documents/QEC/nv_levels_sym/Transitions_Bx_dependence_Ex_'+str(Ex)+'_Bz_'+str(Bz)+'.png')

def plot_transitions_E_dependence(Bz=300.):
	e_range=np.linspace(0,10,100) #gauss
	no_transitions=18

	spectrum=np.zeros((no_transitions,))
	plt.figure()
	for Ex in e_range:
		spectrum=np.vstack((spectrum,nvlevels.get_optical_transitions(
															show_E_transitions=True,
															show_A_transitions=True,
															show_FB_E_transitions=True, 
                        									show_FB_A_transitions=True, 
                        									show_E_prime_flip_transitions=True,
															E_field=[Ex,0.,0.], 
															B_field=[0,0.,Bz],
															Ee0=-1.94,
															)))
	spectrum=spectrum[1:]
	# print spectrum
	# print len(spectrum)
	for i in range(no_transitions):
		if i < 4:
			style = 2
		else: style =0.5
		plt.plot(e_range,spectrum[:,i],linewidth = style)
		plt.title('Transitions E dependence, Bz = '+str(Bz))
		plt.xlabel('Strain E (GHz)')
		plt.ylabel('relative energy difference (GHz)')
		plt.savefig('D:/jcramer3/My Documents/QEC/nv_levels_sym/Transitions_E_dependence_Bz_'+str(Bz)+'.png')

def plot_transitions_in_laserscan_Ex_Ey(Ex,Ey,height=1,B_field = [0.,0.,300.]):
	x2,y2 = nvlevels.get_transitions_ExEy_plottable(Ex,Ey,height,B_field=B_field)
	plt.plot(x2,y2)


# if __name__=='__main__':
# 	plot_ES_e_dependence()
# 	figure()
# 	plot_transitions_b_dependence()
