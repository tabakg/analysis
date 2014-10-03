
# Notebook of changes to the analysis/simulation code
#------------------------------------------------------
#
#8 aug: 	now I change the average phase distribution to a protocol, where I calculate the variance
#       	over a certain nr of reps, and then average over multiple magnetic fields
#9 aug: 	deleted all parts relative to previous approach based on average probability distribution
#10 aug: 	solved bug related to copy to old p_k when 
#11 aug:	add imperfect read-out in estimation optimal phase Cappellaro
#12 aug:	implemented dictionary with multiplicities to analyze results faster
#12 aug-B:	more elegant way to implement Cappellaro protocol, with separate bayesian-update function
#14 aug:	generation of adaptive tables, analysis experimental data

import numpy as np
from analysis.lib.fitting import fit, ramsey, common
from analysis.lib.tools import plot
import random
from matplotlib import rc, cm
import os, sys
import h5py
import logging, time

from matplotlib import pyplot as plt
from analysis.lib import fitting
from analysis.lib.m2.ssro import sequence
from analysis.lib.tools import toolbox
from analysis.lib.fitting import fit,esr
from analysis.lib.tools import plot
from matplotlib import rc, cm

reload(sequence)

class compare_functions ():

	def __init__(self):
		self.data = {}
		self.counter = 0 
		self.xlabel = ''
		self.ylabel = ''
		self.title = ''
		self.log_plot = False
		
	def add (self, x, y, legend):
		self.counter = self.counter+1
		self.data['x_'+str(self.counter)]=x
		self.data['y_'+str(self.counter)]=y
		self.data['l_'+str(self.counter)]=legend
	
	def plot (self, numbers = None):
			
		if (numbers==None):
			numbers = np.arange(self.counter)+1
		
		colors = cm.gist_heat(np.linspace(0., 0.8, len(numbers)))

		ind = 0 
		for i in numbers:	
			if self.log_plot:	
				plt.loglog (self.data['x_'+str(i)], self.data['y_'+str(i)], label = self.data['l_'+str(i)], color = colors[ind]) 
			else:
				plt.plot (self.data['x_'+str(i)], self.data['y_'+str(i)], label = self.data['l_'+str(i)], color = colors[ind]) 
			ind = ind + 1

		x0 = self.data['x_1']
		y0 = self.data['y_1']
		y = y0[0]/(x0/x0[0])
		
		plt.plot (x0, y, ':k')	
		plt.xlabel (self.xlabel)
		plt.ylabel (self.ylabel)
		plt.title (self.title)
		plt.legend()
		plt.show()

	def pdf_statistics (self, numbers = None, N = None, M = None, t0 = None):
		
		self.N = N
		self.M = M
		self.t0 = t0
		m = []
		n = []
		v = []
		vH = []

		
		if (numbers==None):
			numbers = np.arange(self.counter)+1
		
		for i in numbers:	
			beta = self.data['x_'+str(i)]
			p = self.data['y_'+str(i)]
			label = self.data['l_'+str(i)]
			p = p/np.sum(p)
			m0 = np.sum(p*beta)
			m.append(m0)
			v0 = np.sum(beta*beta*p)-m0**2
			v.append(v0)
			vH.append ((np.abs(np.sum(p*np.exp(1j*(2*np.pi*beta*self.t0)))))**(-2)-1)
			
		self.mean = np.squeeze(np.array(m))
		self.var = np.squeeze(np.array(v))
		self.holevo_var = np.squeeze(np.array(vH))
		self.T = self.M*self.t0*(2**(self.N+1)-1)

	
class RamseySequence():

	def __init__ (self, N_msmnts, reps, tau0):
		self.N = N_msmnts
		self.points = 2**(self.N+1)+3
		self.discr_steps = 2*self.points+1
		self.p_k = np.zeros (self.discr_steps)+1j*np.zeros (self.discr_steps)
		self.msmnt_results = None
		self.msmnt_phases = None
		self.msmnt_times = None
		self.T2 = 4452e-9
		self.fid0 = 0.85
		self.fid1 = 0.015
		self.theta = 0*np.pi/180.
		self.t0 = tau0
		self.B_max = 1./(2*tau0)
		self.curr_rep = 0
		self.n_points = 2**(self.N+3)
		self.curr_msmnt = 1
		self.reps = reps
		self.N_total = self.N
		self.M=1
		self.p_k[self.points] = 1/(2.*np.pi)
		self.verbose = True
		self.use_ROfid_in_update = False
		self.renorm_ssro = False
		self.maj_reps = None
		self.maj_thr = None
		self.set_detuning = None
		
	def set_ideal (self):
		self.T2 = 1000.
		self.fid0 = 1.
		self.fid1 = 0.
	
	def field_values_MHz (self):
		return 1e-6*np.linspace (-self.B_max, self.B_max, self.n_points)
		
	def reset (self):
		self.p_k = np.zeros (self.discr_steps)+1j*np.zeros (self.discr_steps)
		self.p_k[self.points] = 1/(2.*np.pi)
			
	def reset_rep_counter(self):
		self.curr_rep = 0
		self.curr_msmnt = 1
		
	def plot_p_k (self):	
		x = np.arange(self.discr_steps)-self.points
		plt.plot (x, np.real (self.p_k))
		plt.plot (x, np.imag (self.p_k))
		plt.xlabel ('k')
		plt.show()

	def bayesian_update(self, m_n, phase_n, t_n,repetition = None):
			
		if (repetition == None):
			repetition = self.curr_rep

		p_old = np.copy(self.p_k)
		
		if self.use_ROfid_in_update:
			p0 = (0.5*self.fid0 + m_n-m_n*self.fid0)*p_old 
			p1 = 0.25*self.fid0*(np.exp(1j*(m_n*np.pi+phase_n))*np.roll(p_old, shift = -t_n)) 
			p2 = 0.25*self.fid0*(np.exp(-1j*(m_n*np.pi+phase_n))*np.roll(p_old, shift = +t_n)) 		
		else:
			p0 = 0.5*p_old 
			p1 = 0.25*(np.exp(1j*(m_n*np.pi+phase_n))*np.roll(p_old, shift = -t_n)) 
			p2 = 0.25*(np.exp(-1j*(m_n*np.pi+phase_n))*np.roll(p_old, shift = +t_n)) 
		p = p0+p1+p2
		p = (p/np.sum(np.abs(p)**2)**0.5)
		self.p_k = np.copy (p)
			
	def inc_rep (self):
		self.curr_rep = self.curr_rep + 1
		if (self.curr_rep>self.reps):
			print 'Maximum repetition reached... Setting counter back to zero!'
			self.curr_rep = 0
			
	def optimal_phase (self):
		ttt = -2**(self.N-self.curr_msmnt+1)
		optimal_phase = 0.5*np.angle (self.p_k[ttt+self.points])
		return optimal_phase
		
	def holevo_variance_pk (self):
		return (2*np.pi*self.p_k[-1+self.points])**(-2)-1.

	def print_msmnt(self):
		print 'Measurement results: ', self.msmnt_results
		print 'Phases: ', self.msmnt_phases
		print 'Ramsey time: ', self.msmnt_times*1e9, 'ns'
		
	def convert_to_dict (self):
		
		self.msmnt_dict = {}
		self.msmnt_multiplicity = {}
		self.phases_dict = {}
		
		ind = 0		
		for j in np.arange(self.reps):
			curr_msmnt = self.msmnt_results [j, :]
			curr_phases = self.msmnt_phases [j, :]
			
			found = 0
			for k in self.msmnt_dict:
				if (np.sum(np.abs(self.msmnt_dict[k]-curr_msmnt))<1e-5):
					self.msmnt_multiplicity[k] = self.msmnt_multiplicity[k]+1
					found = 1
					
			if (found == 0):
				self.msmnt_dict[ind] = curr_msmnt
				self.phases_dict[ind] = curr_phases
				self.msmnt_multiplicity[ind] = 1
				ind = ind+1

	def analysis (self, corrected=True, N_max = None, repetition = None):
		#assumes in each adptv step, we store the number of ones, out of M msmnts (M>1, potentially)
		if (N_max==None):
			N_max = self.N
								
		if (repetition == None):
			repetition = self.curr_rep
			
		prob = np.ones(self.n_points)
		beta = np.linspace (-self.B_max, self.B_max, self.n_points)

		print 'Analysis msmnt results:'
		print self.msmnt_results[repetition, :]

		for n in np.arange(N_max) +(self.N-N_max):
			q = 2*np.pi*beta*self.msmnt_times[n]*self.t0+self.msmnt_phases[repetition, n]
			dec = np.exp(-(self.msmnt_times[n]*self.t0/self.T2)**2)
			nr_ones = self.msmnt_results[repetition, n]
			nr_zeros = self.M-nr_ones
			
			#print 'Bayesian update: '+str(nr_zeros)+' zeros and '+str(nr_ones)+' ones.'  

			for j in np.arange(nr_ones):
				prob = prob*(1-dec*np.cos(q))
			for j in np.arange(nr_zeros):
				prob = prob*(1+dec*np.cos(q))

			#for j in np.arange(nr_ones):
			#	prob = prob*self.fid0*(1-dec*np.cos(q))
			#for j in np.arange(nr_zeros):
			#	prob = prob*((1-0.5*self.fid0)+0.5*self.fid0*dec*np.cos(q))

			
		prob = prob/np.sum(np.abs(prob))
		return beta, prob


	def analysis_dict (self, phase=[], msmnt_results=[], times=[]):
		#assumes in each adptv step, we store the number of ones, out of M msmnts (M>1, potentially)
			
		prob = np.ones(self.n_points)
		beta = np.linspace (-self.B_max, self.B_max, self.n_points)
		N_max = len(msmnt_results)
		for n in np.arange(N_max) +(self.N-N_max):
			q = 2*np.pi*beta*times[n]*self.t0+phase[n]
			dec = np.exp(-(times[n]*self.t0/self.T2)**2)
			nr_ones = msmnt_results[n]
			nr_zeros = self.M-nr_ones

			for j in np.arange(nr_ones):
				prob = prob*(1-dec*np.cos(q))
			for j in np.arange(nr_zeros):
				prob = prob*(1+dec*np.cos(q))
		prob = prob/np.sum(np.abs(prob))
		return beta, prob

	def plot_phase_distribution (self, repetition = 0):
		beta, prob = self.analysis (corrected=False, repetition = repetition)
		plt.plot (beta*1e-6, prob)
		plt.xlim([-20,20])
		plt.show()
		
	def mean_square_error (self, set_value = None, do_plot=False, save_plot=False, xlim = None):
		
		msqe = 0
		total_reps = 0

		if (set_value==None):
			set_value = self.set_detuning
		
		for k in self.msmnt_dict:
			curr_phase = self.phases_dict[k]
			curr_msmnt = self.msmnt_dict[k]
			mult = self.msmnt_multiplicity[k]

			beta, prob = self.analysis_dict (phase = curr_phase, msmnt_results = curr_msmnt, times = self.msmnt_times)
			
			fase = np.exp(1j*2*np.pi*beta*self.t0)
			phi_m = np.sum(fase*prob)

			if (total_reps==0):
				avg_prob = mult*prob
			else:
				avg_prob = avg_prob + mult*prob
			
			phi_set = np.exp(1j*2*np.pi*set_value*self.t0)
			msqe = msqe + mult*(phi_m/phi_set)
			total_reps = total_reps + mult
		
		avg_prob = avg_prob/np.sum(avg_prob)
		msqe = msqe/float(total_reps)
		msqe = np.abs(msqe)**(-2)-1

		if do_plot:
			f1 = plt.figure()
			plt.plot (beta/1e6, avg_prob)
			plt.xlabel ('magnetic field detuning [MHz]')
			plt.ylabel ('prob distrib')
			plt.title('msqe = '+str(msqe))
			if not(xlim==None):
				plt.xlim(xlim)

			if save_plot:
				f_name = 'prob_distr.png'
				savepath = os.path.join(self.folder, f_name)
				f1.savefig(savepath)
			plt.show()

		return beta, avg_prob, msqe

	def print_results (self):

		print '---    Measurement results  - SUMMARY    ---'
		print '--------------------------------------------'
		
		for k in self.msmnt_dict:
			curr_phase = self.phases_dict[k]
			curr_msmnt = self.msmnt_dict[k]
			mult = self.msmnt_multiplicity[k]

			print '(*)', curr_msmnt, ' - ', mult, ' times' 
		print '--------------------------------------------'


	def hist_phases (self):

		for i in np.arange (self.N_total):
			a = self.msmnt_phases [:,i]*180/np.pi
			plt.hist (a, 30)
			plt.title ('msmnt step nr. ' +str(i+1))
			plt.xlabel ('adaptive phase [deg]')
			plt.show()

	def print_phases(self):
		for i in np.arange (self.N_total):
			print '------------------------------------------'
			print ' Msmnt nr. '+str(i+1)
			print np.unique(self.msmnt_phases [:,i]*180/np.pi)


class RamseySequence_Simulation (RamseySequence):

	def setup_simulation(self, magnetic_field_hz = 0., M = 1):
		self.beta_sim = magnetic_field_hz
		self.M = M

	def save_folder (self, folder = '/home/cristian/Work/Research/adaptive magnetometry/'):
		self.save_folder = folder
	
	def ramsey (self, t=0., theta=0.):

		n0 = 0.5*(1-np.cos(2*np.pi*self.beta_sim*t+theta))
		n1 = 0.5*(1+np.cos(2*np.pi*self.beta_sim*t+theta))
	
		pp0 = self.fid0*n0+self.fid1
		pp1 = n1+(1-self.fid0*n0)
		p0 = pp0/(pp0+pp1)
		p1 = pp1/(pp0+pp1)
		np.random.seed()
		result = 1-np.random.choice (2, 1, p=[p0, p1])
		return result[0]		
		
	def majority_vote_msmnt (self, theta_n, t_n):
	
		m_total = 0
		for m in np.arange (self.maj_reps):
			res = self.ramsey (theta=theta_n, t = t_n*self.t0)
			m_total = m_total + res
		m_total = round(m_total/self.fid0)
		if (m_total>self.maj_thr):
			m_res = 1
		else:
			m_res = 0	
		return m_res

	def M_ssro_msmnt (self, theta_n, t_n):
		m_total = 0
		for m in np.arange (self.M)+1:
			res = self.ramsey (theta=theta_n, t = t_n*self.t0)
			m_total = m_total + res
			
		n_ones = m_total
		if self.renorm_ssro:
			n_ones = round(m_total/self.fid0)
			if (n_ones>self.M):
				n_ones = self.M
		return n_ones, self.M-n_ones

	def sim_cappellaro (self):
		
		if self.verbose:				
			print '----------------------------------'
			print 'Simulating Cappellaro protocol'
			print '----------------------------------'
			print '- N = '+str(self.N)+ ', M = '+str(self.M)

		self.msmnt_phases = np.zeros((self.reps,self.N))
		self.msmnt_times = np.zeros(self.N)
		self.msmnt_results = np.zeros((self.reps,self.N))
		
		nn = np.arange(self.N)+1
		tau = 2**(self.N-nn)
		self.msmnt_times = tau
		self.reset_rep_counter()
		ex
		for r in np.arange(self.reps):

			msmnt_results = np.zeros (self.N)
			t = np.zeros (self.N)
			phase = np.zeros(self.N)
			self.p_k = np.zeros (self.discr_steps)+1j*np.zeros (self.discr_steps)
			self.p_k [self.points] = 1/(2.*np.pi)
	
			for n in np.arange(self.N)+1:

				t[n-1] = int(2**(self.N-n))
				ttt = -2**(self.N-n+1)
				phase[n-1] = 0.5*np.angle (self.p_k[ttt+self.points])

				n_ones, n_zeros = self.M_ssro_msmnt (theta_n = phase[n-1], t_n = t[n-1])
				
				for jj in np.arange(n_ones):
					self.bayesian_update (m_n = 1, phase_n = phase[n-1], t_n = 2**(self.N-n))

				for jj in np.arange(n_zeros):
					self.bayesian_update (m_n = 0, phase_n = phase[n-1], t_n = 2**(self.N-n))
			
				msmnt_results[n-1] = n_ones
				
			self.msmnt_results [r, :] = np.copy(msmnt_results)
			self.msmnt_phases [r, :] = np.copy(phase)
			self.inc_rep()

	def sim_cappellaro_majority (self):
		
		if self.verbose:				
			print '-----------------------------------------'
			print 'Simulating Cappellaro protocol (maj vote)'
			print '-----------------------------------------'
			print '- N = '+str(self.N)+ ', M = '+str(self.M)

		self.msmnt_phases = np.zeros((self.reps,self.N))
		self.msmnt_times = np.zeros(self.N)
		self.msmnt_results = np.zeros((self.reps,self.N))
		
		nn = np.arange(self.N)+1
		tau = 2**(self.N-nn)
		self.msmnt_times = tau
		self.reset_rep_counter()
		
		for r in np.arange(self.reps):

			msmnt_results = np.zeros (self.N)
			t = np.zeros (self.N)
			phase = np.zeros(self.N)
			self.p_k = np.zeros (self.discr_steps)+1j*np.zeros (self.discr_steps)
			self.p_k [self.points] = 1/(2.*np.pi)
	
			for n in np.arange(self.N)+1:

				t[n-1] = int(2**(self.N-n))
				ttt = -2**(self.N-n+1)
				phase[n-1] = 0.5*np.angle (self.p_k[ttt+self.points])

				m_total = 0
				for m in np.arange(self.M):
					m_res = self.majority_vote_msmnt (theta_n = phase[n-1], t_n = t[n-1])				
					self.bayesian_update (m_n = m_res, phase_n = phase[n-1], t_n = 2**(self.N-n))
					m_total = m_total + m_res
				msmnt_results[n-1] =m_total
				
			self.msmnt_results [r, :] = np.copy(msmnt_results)
			self.msmnt_phases [r, :] = np.copy(phase)
			self.inc_rep()
			
	def load_table (self, N, M):
		
		self.table_folder = '/home/cristian/Work/Research/adaptive magnetometry/adaptive_tables/NewTables/'
		name = 'adptv_table_cappellaro_N='+str(self.N)+'_M='+str(self.M)+'.npz'
		a = np.load(self.table_folder+name)
		self.table = a['table']


	def table_based_simulation (self):
	
		if (self.maj_reps == None):
			print 'Majority reps value not set!'
			a = raw_input ('Set it now...')
			self.maj_reps = a
			self.maj_thr = 0
		
		if self.verbose:				
			print '--------------------------------------------'
			print 'Simulating Cappellaro protocol (table-based)'
			print '--------------------------------------------'
			print '- N = '+str(self.N)+ ', M = '+str(self.M)

		self.msmnt_phases = np.zeros((self.reps,self.N))
		self.msmnt_times = np.zeros(self.N)
		self.msmnt_results = np.zeros((self.reps,self.N))
		
		nn = np.arange(self.N)+1
		tau = 2**(self.N-nn)
		self.msmnt_times = tau
		self.reset_rep_counter()
		self.load_table (N=self.N, M=self.M)
		
		for r in np.arange(self.reps):

			msmnt_results = np.zeros (self.N)
			t = np.zeros (self.N)
			phase = np.zeros(self.N)
	
			for n in np.arange(self.N)+1:
						
				if (n==1):
					pp0 = 1
				else:
					pp0 = 1+((self.M+1)**(n-1))/self.M
				pp1 = 0
				for j in np.arange(n-1):
					pp1 = pp1 + msmnt_results[j]*((self.M+1)**j)
				pos = pp0 + pp1
				phase[n-1] = self.table[pos-1]*np.pi/180.
				phase[0]=0

				m_total = 0
				for m in np.arange(self.M):
					m_res = self.majority_vote_msmnt (theta_n = phase[n-1], t_n = 2**(self.N-n))				
					self.bayesian_update (m_n = m_res, phase_n = phase[n-1], t_n = 2**(self.N-n))
					m_total = m_total + m_res
				msmnt_results[n-1] = m_total
				
			self.msmnt_results [r, :] = np.copy(msmnt_results)
			self.msmnt_phases [r, :] = np.copy(phase)
			self.inc_rep()


					
	def save (self, name):
		
		np.savez (self.folder+name+'.npz', msmnt_results = self.msmnt_results, msmnt_times = self.msmnt_times, msmnt_phases=self.msmnt_phases,
					T2=self.T2, fid0=self.fid0, fid1=self.fid1, B_sim = self.beta_sim, tau0 =self.t0, N=self.N, reps = self.reps)
		
	def load (self, name):
		a = np.load (self.folder+name+'.npz')
		self.msmnt_results = a['msmnt_results']
		self.msmnt_times = a['msmnt_times']
		self.msmnt_phases = a['msmnt+phases']
		self.T2 = a['T2']
		self.fid0 = a['fid0']
		self.fid1 = a['fid1']
		self.beta_sim = a['B_sim']
		self.t0 = a['tau0']
		self.N = a['N']
		self.reps = a[ 'reps']
		self.points = 2**(self.N)+3
		self.discr_steps = 2*self.points+1
		self.p_k = np.zeros ((reps,self.discr_steps))+1j*np.zeros ((reps, self.discr_steps))
		self.theta = 0*np.pi/180.
		self.B_max = 1./(2*self.t0)
		self.curr_rep = 0
		self.n_points = 50000
		self.curr_msmnt = 1
		
		for i in np.arange(reps):
			self.p_k[i, self.points] = 1/(2.*np.pi)
		
		print 'Data loaded!'		


class RamseySequence_Exp (RamseySequence):

	def __init__ (self, folder = '', sub_string = ''):
		self.folder = folder
		self.sub_string = sub_string
		self.t0 = 1e-9
		self.n_points = 50000
		self.B_max = 1./(2*self.t0)
		
	def set_exp_pars(self, T2, fid0, fid1):
		self.T2=T2
		self.fid0 = fid0
		self.fid1 = fid1

	def load_exp_data (self):

		a = sequence.SequenceAnalysis(self.folder)
		a.get_sweep_pts()
		a.get_magnetometry_data(name='adwindata', ssro = False)
		self.msmnt_results = a.clicks
		self.reps, self.N = np.shape (a.clicks)
		self.t0 = a.t0
		self.msmnt_times = np.zeros(len(a.ramsey_time))
		self.set_detuning = a.set_detuning
		for j in np.arange(len(a.ramsey_time)):
			self.msmnt_times[j] = a.ramsey_time[j]/self.t0
		self.msmnt_phases = 2*np.pi*a.set_phase/255.
		self.M=a.M
		#print ' ---- phases_detuning' 
		#print a.phases_detuning	
		print ' ---- Set phases -----'
		print np.unique (self.msmnt_phases*180/np.pi)
		print ''
		
		phases_detuning = 2*np.pi*a.phases_detuning/360.
		b = np.ones(self.reps)
		self.msmnt_phases = np.mod(self.msmnt_phases - np.outer (b, phases_detuning), 2*np.pi)



class AdaptiveTable ():

	def __init__(self, N, M):
		self.N = N
		self.M = M 
		self.T2 = 4400e-9
		self.t0 = 1e-9
		
		self.table = None
		self.test_pp1 = None
		self.test_pp0 = None
		self.max_element = None
		
		self.verbose = False
		self.save_folder = '/home/cristian/Work/Research/adaptive magnetometry/adaptive_tables/NewTables_2/'


	def M_conv (self, element = 1):
	
		#print 'conversion decimal to '+str(M+1)+'-ary'
		msmnt_results = np.zeros(self.N)
		a = element
		for k in np.arange(self.N-1)+1:
			msmnt_results [self.N-k] = np.mod(a,self.M+1)
			a = a/(self.M+1)
		return msmnt_results[1:]

	
	def generate (self):
	
		total_length = int(((self.M+1)**(self.N)-1)/self.M)+1

		self.table = np.zeros(total_length)
		self.test_pp1 = np.zeros(total_length)
		self.test_pp0 = np.zeros(total_length)
		self.max_element = (self.M+1)**(self.N-1)
		print 'Total length array: ', total_length
		print 'Sweeping between 0... '+str(self.max_element-1)
				
		for j in np.arange (self.max_element):
		
			self.curr_j = j
			
			seq = RamseySequence_Simulation (N_msmnts = self.N, reps=1, tau0=1e-9)
			seq.M = self.M
			msmnt_results = self.M_conv (element=j)
	
			phase = np.zeros(self.N)
			seq.p_k = np.zeros (seq.discr_steps)+1j*np.zeros (seq.discr_steps)
			seq.p_k [seq.points] = 1/(2.*np.pi)
	
			#n is the msmnt currently being performed
			opt_phase = 0.
			optimal_phases = []
			summary_pp0 = []
			summary_pp1 = []
			for n in np.arange(self.N-1)+2:
				
				seq.bayesian_update (m_n = msmnt_results[n-2], phase_n = opt_phase, t_n = 2**(self.N-(n-1)))
				ttt = -2**(self.N-(n-1))
				opt_phase = 0.5*np.angle (seq.p_k[ttt+seq.points])
				optimal_phases.append(np.round(opt_phase*180/np.pi))

				pp0 = 1+((((self.M+1)**(n-1))-1)/self.M)
				pp1 = 0
				for i in np.arange(n-1):
					pp1 = pp1+msmnt_results[i]*(self.M+1)**(i)			
				position = pp0+pp1
				summary_pp0.append(pp0)
				summary_pp1.append(pp1)				

				self.table[position] = opt_phase*180/np.pi
				self.test_pp0[position] = pp0
				self.test_pp1[position] = pp1
				
			if self.verbose:
				print '   ----- Analyzing round ' +str(j)
				print '      msmnt results: ', msmnt_results
				print '      optimal phases: ', optimal_phases
				print '      stored in positions: pp0 = ', summary_pp0
				print '                           pp1 = ', summary_pp1
				print '                           pos = ', np.array(summary_pp1)+np.array(summary_pp0)
				
				
		#adwin basic counts arrays elements starting from 1:			
		self.table = self.table[1:]
		self.test_pp0 = self.test_pp0[1:]
		self.test_pp1 = self.test_pp1[1:]

	def save_table(self, label=''):
		
		name = 'adptv_table_cappellaro_N='+str(self.N)+'_M='+str(self.M)+label+'.npz'
		np.savez (self.save_folder+name, table = self.table, N=self.N, M=self.M, T2=self.T2, t0=self.t0)
		

class AdaptiveMagnetometry ():

	def __init__(self, N, t0, reps):
		self.N = N
		self.t0 = t0
		self.reps = reps
		self.B_max = 1./(2*t0)
		self.n_points = 2**(self.N+3)
		self.nr_B_points = 2**(self.N+2)/2
		self.results = np.zeros((self.N, self.nr_B_points))
		
		self.msmnt_results = None
		self.msmnt_phases = None
		self.msmnt_times = None
		
	def set_exp_params(self, T2 = 4452e-9, fid0 = 0.85, fid1 = 0.015):
		self.T2 = T2
		self.fid0 = fid0
		self.fid1 = fid1
		
	def set_protocol (self, M=1, renorm_ssro = False, maj_reps = None, maj_thr = None):
		self.M=M
		self.theta = 0*np.pi/180.
		self.use_ROfid_in_update = False
		self.renorm_ssro = renorm_ssro
		self.maj_reps = maj_reps
		self.maj_thr = maj_thr
		
	def sweep_field_fixedN (self, N = None, do_simulate = True):
	
		if (N==None):
			N = self.N
			
		self.B_values = np.linspace(0, self.B_max/2., self.nr_B_points)
		ind = 0
		print 'Processing: N = '+str(N), ' (M='+str(self.M)+')'
		for b in self.B_values:
		
			if do_simulate: 
				s = RamseySequence_Simulation (N_msmnts = N, reps=self.reps, tau0=self.t0)
				s.setup_simulation (magnetic_field_hz = b, M=self.M)
				s.B_max = 500e6
				s.verbose = False
				s.T2 = self.T2
				s.fid0 = self.fid0
				s.fid1 = self.fid1
				s.renorm_ssro = self.renorm_ssro
				s.maj_reps = self.maj_reps
				s.maj_thr = self.maj_thr
				s.table_based_simulation ()
			else:
				label = 'N='+str(N)+'_M='+str(self.M)+'_B='+str(b)
				f = toolbox.latest_data(contains=label)
				s = RamseySequence_Exp (folder = f)
				s.set_exp_pars (T2=4000e-9, fid0=0.85, fid1=0.015)
				s.load_data()
			s.convert_to_dict()
			beta, p, err = s.mean_square_error(set_value=b)
			self.results[N-1, ind] = err**0.5
			ind =ind+1
			
	def sweep_field (self, do_simulate = True):
	
		for n in np.arange(self.N)+1:
			self.sweep_field_fixedN (N=n, do_simulate = do_simulate)
			
	def plot_msqe (self):
		r = compare_functions()	
		r.xlabel = 'field [MHz]'
		r.ylabel = 'mean square error'
		r.title = 'N = '+str(self.N)+', M = '+str(self.M)+', sweep magnetic field'
		for n in np.arange(self.N):
			r.add (x=self.B_values/1e6, y=self.results[n, :], legend = str(n+1))
		r.plot()


	def scaling (self):
		self.scaling_variance = np.zeros(self.N)
		self.total_time = np.zeros(self.N)

		for n in np.arange(self.N)+1:
			s = self.results[n-1, :]
			self.scaling_variance [n-1] = np.mean(s**2)
			self.total_time [n-1] = self.M*self.maj_reps*(2**(n+1)-1)
		
		self.plot_scaling()
			
	def plot_scaling(self):
		
		if (self.scaling_variance==None):
			self.scaling()

		plt.figure()
		plt.loglog (self.total_time*self.t0/1000., self.scaling_variance*self.total_time, 'b')
		plt.loglog (self.total_time*self.t0/1000., self.scaling_variance*self.total_time, 'ob')
		plt.xlabel ('total ramsey time')
		plt.ylabel ('$V_H*T$')
		plt.show()
		
	def save(self, folder = None):
		
		if (folder==None):
			self.folder = '/home/cristian/Work/Research/adaptive magnetometry/simulations/adaptive_protocol/12aug/'
		else:
			self.folder = folder

		fName = 'simulation_N='+str(self.N)+'_M='+str(self.M)+'.npz'
		np.savez(self.folder+fName, B_field=self.B_values, results =self.results, 
					total_time = self.total_time, scaling_variance = self.scaling_variance) 
	

def analysis_exp():
	f = toolbox.latest_data(contains='220832')
	s = RamseySequence_Exp (folder = f)
	s.set_exp_pars (T2=4000e-9, fid0=0.85, fid1=0.015)
	#s.M=1
	#s.set_ideal()
	s.load_data()
	p = s.plot_avg_phase_distribution()
	#s.print_phases()
	p = s.phase_distribution_scaling (do_plot=True)
	p.plot_scaling()

	

#exp = AdaptiveMagnetometry (N=6, reps = 100, t0=1e-9)
#exp.set_exp_params(T2 = 4452., fid0 = 1., fid1 = 0.)
#exp.set_protocol (M=3, renorm_ssro = True, maj_reps = 3, maj_thr = 0)
#exp.sweep_field()
#exp.plot_msqe()
#exp.scaling()
#exp.save()
#potrei plottare anche la distribuzione di probabilita mediata su diverse implementazioni


'''
for n in np.arange(10)+1:
	for m in np.arange(7)+1:
		
		print '##### N = '+str(n)+' --- M = '+str(m)
		
		t = AdaptiveTable (N=6,M=3)
		t.verbose = False
		t.generate()
		t.save_table()
'''


'''
bbb = -0*4*93.285e6
maj_reps = 3
s = RamseySequence_Simulation (N_msmnts = 6, reps=100, tau0=1e-9)
s.B_max = 600e6
std = []
thresholds = []
#for thr in [0, 1,2, 3]:
s.setup_simulation (magnetic_field_hz = bbb, M=3)
s.T2 = 4000e-9
s.fid0 = 1#0.85
s.fid1 = 0#0.02
s.renorm_ssro = False
s.maj_reps = maj_reps
s.maj_thr = 0
s.table_based_simulation()
s.convert_to_dict()
	
beta, p, err = s.mean_square_error(set_value=bbb)
plt.plot (beta*1e-6, p, linewidth =1.5)
#media = np.sum (beta*p)
#v = np.sum(beta*beta*p)-media**2
#	std.append((v**0.5)*1e-6)
plt.xlabel ('magnetic field [MHz]')
plt.legend()
plt.show()
'''


'''
plt.plot (thresholds, std)
plt.plot (thresholds, std, 'ob')
	thresholds.append(thr)
plt.title ('majority reps: '+str(maj_reps))
plt.xlabel ('threshold')
plt.ylabel ('std [MHz]')
plt.show()
'''


f = toolbox.latest_data(contains='adptv_estimation_det')
s = RamseySequence_Exp (folder = f)
s.set_exp_pars (T2=96e-6, fid0=0.85, fid1=0.015)
print f
s.load_exp_data()
#print np.mod(s.msmnt_phases, 2*np.pi)*360./(2*np.pi)
#s.msmnt_phases = np.zeros(np.shape(s.msmnt_phases))
s.convert_to_dict()
s.print_results()
#s.plot_phase_distribution(repetition = 0)
beta, prob, err = s.mean_square_error(do_plot=True, save_plot=True)

#b, p = s.analysis_dict (phase = [0,0,0,0,0,0,0,0], msmnt_results =[0,0,0,0,0,0,0,0], times = s.msmnt_times)
#plt.plot (b, p)
#plt.show()



