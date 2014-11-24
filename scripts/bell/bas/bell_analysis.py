f=h5py.File(r'K:\ns\qt\Diamond\Documents\Documents Just\MBD\After2014-11-19analysis\Total_Bell_events.hdf5','r')
g=f['analysis']['Total_Bell_events']
d=g.value
cs=g.attrs['Columns'].split(', ')
f.close()

sn   		= 0	#d[:,0]
st_1 		= 1	#d[:,1]
st_2 		= 2	#d[:,2]
ch_1 		= 3	#d[:,3]
ch_2  		= 4	#d[:,4]
psi_min     = 5
t  	 		= 6	#d[:,6]
sn_lt3		= 7	#d[:,7]
no_ph_lt3	= 9	#d[:,8]
rnd_lt3		= 11	#d[:,10]
st_rnd_lt3  = 12  #d[:,11] #currently wrong
sn_lt4		= 37	#d[:,36]
no_ph_lt4	= 39	#d[:,37]
rnd_lt4		= 41	#d[:,39]
st_rnd_lt4  = 42  #d[:,40] #currently wrong

noof_ev=len(d)
print 'noof events {}'.format(noof_ev)
#sanity checks
ro_ms0_lt3=np.sum(d[:,no_ph_lt3]>0)/float(noof_ev)
ro_ms0_lt4=np.sum(d[:,no_ph_lt4]>0)/float(noof_ev)
print 'RO ms=0 LT3: {:.2f}%, RO ms=0 LT4: {:.2f}% '.format(ro_ms0_lt3*100,ro_ms0_lt4*100 )

rnd_0_lt3=np.sum(d[:,rnd_lt3]==0)/float(noof_ev)
rnd_0_lt4=np.sum(d[:,rnd_lt4]==0)/float(noof_ev)
print 'RND0 LT3: {:.2f}%, RND0 LT4: {:.2f}% '.format(rnd_0_lt3*100,rnd_0_lt4*100 )
print 'no of RND errors: {} '.format(np.sum(d[:,rnd_lt3]>1)+np.sum(d[:,rnd_lt4]>1))

pts=15
X=np.linspace(1000,100000,pts)
Y=np.zeros((pts,2))
T=np.zeros((pts,2))
for k,x in enumerate(X):
	#tail/laser filter
	st_start_ch0 = 5445000
	st_len   = 40000 #50 ns
	ch0_ch1_diff = 600 #1 ns
	st_start_ch1=st_start_ch0 + ch0_ch1_diff
	p_sep = 600000 #600 ns
	st_fltr = (((st_start_ch0<=d[:,st_1])       & (d[:,st_1]<(st_start_ch0+st_len)) 	  & (d[:,ch_1]==0)) | ((st_start_ch1<=d[:,st_1]) 	   & (d[:,st_1]<(st_start_ch1+st_len)) 		 & (d[:,ch_1]==1)) )  \
			& (((st_start_ch0+p_sep<=d[:,st_2]) & (d[:,st_2]<(st_start_ch0+p_sep+st_len)) & (d[:,ch_2]==0)) | ((st_start_ch1+p_sep<=d[:,st_2]) & (d[:,st_2]<(st_start_ch1+p_sep+st_len)) & (d[:,ch_2]==1)) )  \

	#dt filter
	dt = x # 10 ns
	dt_fltr = np.abs(np.array(d[:,st_2] - d[:,st_1], dtype='int')-p_sep) < dt 
	#print np.abs(np.array(d[:,st_2] - d[:,st_1], dtype='int')-p_sep)
	#psi_min_plus_filter
	psi_min_fltr = d[:,ch_1] != d[:,ch_2] #(d[:,ch_1]==0) & (d[:,ch_2]==) 
	psi_plus_fltr= d[:,ch_1] == d[:,ch_2] #(d[:,ch_1]==1) & (d[:,ch_2]==1) 
	#psi_x sanity check:
	#print 'PSI MIN check',np.sum(psi_min_fltr), np.sum(d[:,psi_min]==1)
	#print 'PSI PLUS check',np.sum(psi_plus_fltr), np.sum(d[:,psi_min]==0)
	#print 'PSI other', np.sum(d[:,psi_min]>1)

	#RND err fvilter
	rnd_fltr= (d[:,rnd_lt3]<2) & (d[:,rnd_lt4]<2)

	#filtered data
	for psi,psi_fltr in zip(['psi_min','psi_plus'],[psi_min_fltr,psi_plus_fltr]):
		fltr = st_fltr & psi_fltr & rnd_fltr & dt_fltr
		d_fltr = d[fltr]
		print '-'*40
		print 'FILTERED EVENTS {} \n  noof events {}\n'.format(psi,len(d_fltr))
		rnd_0_lt3=np.sum(d_fltr[:,rnd_lt3]==0)/float(len(d_fltr))
		rnd_0_lt4=np.sum(d_fltr[:,rnd_lt4]==0)/float(len(d_fltr))
		#print 'RND0 LT3: {:.2f}%, RND0 LT4: {:.2f}% '.format(rnd_0_lt3*100,rnd_0_lt4*100 )
		#print 'no of RND errors: {} '.format(np.sum(d_fltr[:,rnd_lt3]>1)+np.sum(d_fltr[:,rnd_lt4]>1))


		rnd_corr=[[0,0],[0,1],[1,0],[1,1]] #'RND [LT3,LT4]'
		ro_corr =[[1,1],[1,0],[0,1],[0,0]] #'RO [LT3,LT4] ms  00, 01, 10, 11'

		corr_mat=np.zeros((4,4))
		Es=np.zeros(4)
		for i,rnd in enumerate(rnd_corr):
			for j,ro in enumerate(ro_corr):
				corr_mat[i,j] = np.sum((d_fltr[:,rnd_lt3] == rnd[0]) \
									 & (d_fltr[:,rnd_lt4] == rnd[1]) \
									 & ((d_fltr[:,no_ph_lt3]>0) == ro[0]) \
									 & ((d_fltr[:,no_ph_lt4]>0) == ro[1]))
				#print 'rnd: {}, ro {}, N {}'.format(rnd,ro,corr_mat[i,j])
			Es[i] = (corr_mat[i,0] - corr_mat[i,1] - corr_mat[i,2] + corr_mat[i,3])/float(np.sum(corr_mat[i,:]))

		print 'RO ms  00, 01, 10, 11'
		print 'RND00', corr_mat[0], '  +pi/2, +3pi/4 (?)'
		print 'RND01', corr_mat[1], '  +pi/2, -3pi/4 (?)'
		print 'RND10', corr_mat[2], '  0,     +3pi/4 (?)'
		print 'RND11', corr_mat[3], '  0,     -3pi/4 (?)'

		print '\n E (00     01    10    11 )'
		print '   ({:.2f}, {:.2f}, {:.2f}, {:.2f})'.format(Es[0],Es[1],Es[2],Es[3])

		if psi == 'psi_min':
			CHSH  = -Es[0] + Es[1] + Es[2] + Es[3]
			Y[k,0]= CHSH
			T[k,0]=len(d_fltr)
		elif psi == 'psi_plus':
			CHSH  = Es[0] - Es[1] + Es[2] + Es[3] 
			Y[k,1]= CHSH
			T[k,1]=len(d_fltr)
		print 'CHSH', CHSH

#figure()
#bins=linspace(5435,5465,300)
#hist(d[d[:,ch_1]==0,st_1]/1000., bins=bins, log=True, color='r', histtype='step')
#hist(d[d[:,ch_1]==1,st_1]/1000., bins=bins, log=True, color='b', histtype='step')
if pts>1:
    figure()
    ax=plt.subplot(111)
    ax.plot(X/1000.,Y[:,0])
    ax.plot(X/1000.,Y[:,1])
    ax2=ax.twinx()
    ax2.plot(X/1000.,T[:,0], color='r')