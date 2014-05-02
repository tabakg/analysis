import numpy as np
import matplotlib.pyplot as plt
import measurement.scripts.lt2_scripts.setup.msmt_params as params


## 
### Data ### 

data = [
0	,2.025315387011e+00,	8.729238017633e-06,	3.729649917332e+00,	8.157289022297e-06,	2.877482652172e+00,	1.331508827911e+00,	3.040742375030e+02,
200	,2.025625388242e+00,	1.194529285777e-05,	3.729435368022e+00,	7.754452164037e-06,	2.877530378132e+00,	5.803352167279e+00,	3.039856930632e+02,
400	,2.025950572128e+00,	8.203601134210e-06,	3.729317011979e+00,	8.175629503676e-06,	2.877633792053e+00,	1.014003851680e+01,	3.039174806975e+02,
600	,2.026546043410e+00,	8.091197085748e-06,	3.728989892844e+00,	7.098297226400e-06,	2.877767968127e+00,	1.387626255976e+01,	3.037670337297e+02,
800	,2.027192125584e+00,	7.707842764761e-06,	3.728698816543e+00,	6.569262524625e-06,	2.877945471064e+00,	1.764315538965e+01,	3.036185428252e+02,
1000	,2.027993366590e+00,	7.655993729716e-06,	3.728360785943e+00,	6.681345823743e-06,	2.878177076267e+00,	2.159268475870e+01,	3.034396676791e+02,
800	,2.026221699481e+00,	7.553363815312e-06,	3.729617162712e+00,	4.735951394831e-06,	2.877919431097e+00,	1.714068275795e+01,	3.039528270007e+02,
600	,2.025436411180e+00,	8.361944941893e-06,	3.730005565383e+00,	6.894999080109e-06,	2.877720988282e+00,	1.269242055909e+01,	3.041412866144e+02,
400	,2.024870835188e+00,	8.163424863165e-06,	3.730289607504e+00,	7.908661698965e-06,	2.877580221346e+00,	8.184656791066e+00,	3.042779966622e+02,
200	,2.024459260973e+00,	9.746964431092e-06,	3.730532546419e+00,	7.705690881559e-06,	2.877495903696e+00,	3.260244408272e+00,	3.043858545642e+02,
0	,2.024219488237e+00,	8.725492512740e-06,	3.730775638644e+00,	7.824168942247e-06,	2.877497563440e+00,	3.426053495176e+00,	3.044721796274e+02,
-200	,2.024360164646e+00,	8.365169683979e-06,	3.730720168143e+00,	7.061994895125e-06,	2.877540166395e+00,	6.341219070260e+00,	3.044416917875e+02,
-400	,2.024818342990e+00,	7.677302824026e-06,	3.730498503938e+00,	6.282034685647e-06,	2.877658423464e+00,	1.092050903298e+01,	3.043329036214e+02,
-600	,2.025577804685e+00,	7.033246525326e-06,	3.730080619426e+00,	5.576599601927e-06,	2.877829212055e+00,	1.527906624024e+01,	3.041408873940e+02,
-800	,2.026538930556e+00,	6.545228929886e-06,	3.729585092246e+00,	5.750967660506e-06,	2.878062011401e+00,	1.972706153580e+01,	3.039055534494e+02,
-1000	,2.027667371995e+00,	8.029855667625e-06,	3.729004416858e+00,	4.803215052433e-06,	2.878335894426e+00,	2.392538259707e+01,	3.036294559272e+02,
-800	,2.027538700660e+00,	7.795242823245e-06,	3.728600711048e+00,	5.080031592355e-06,	2.878069705854e+00,	1.985926595779e+01,	3.035522967246e+02,
-600	,2.026744421614e+00,	6.555573632737e-06,	3.728977391812e+00,	5.162684588996e-06,	2.877860906713e+00,	1.595946309087e+01,	3.037392156046e+02,
-400	,2.026032503415e+00,	6.621479382337e-06,	3.729334394448e+00,	6.276868378180e-06,	2.877683448931e+00,	1.166282656140e+01,	3.039112080366e+02,
-200	,2.025434179884e+00,	7.682235651728e-06,	3.729699807384e+00,	6.456040401121e-06,	2.877566993634e+00,	7.625913132415e+00,	3.040708567068e+02,
0	,2.025175849356e+00,	8.810433850271e-06,	3.729836476809e+00,	8.469251864807e-06,	2.877506163083e+00,	4.181966994388e+00,	3.041349022016e+02]
'''
data = [0	,2.025171839704e+00,	8.199869797713e-06,	3.729823984980e+00,	7.039612443540e-06,	2.877497912342e+00,	3.460287816958e+00,	3.041325168158e+02,
150	,2.025251802830e+00,	8.389336670319e-06,	3.729711918316e+00,	7.413254877634e-06,	2.877481860573e+00,	1.115227503053e+00,	3.040965597834e+02,
300	,2.025445253753e+00,	7.993392639593e-06,	3.729539131946e+00,	6.555009906012e-06,	2.877492192849e+00,	2.854973645809e+00,	3.040323102607e+02,
150	,2.024394844159e+00,	8.253477344972e-06,	3.730572769672e+00,	6.015549787363e-06,	2.877483806915e+00,	1.595088254445e+00,	3.044032440306e+02,
0	,2.024320411172e+00,	9.593341221051e-06,	3.730718081992e+00,	6.422674588306e-06,	2.877519246582e+00,	5.121473992173e+00,	3.044461988855e+02,
-150	,2.024522278213e+00,	7.086406522709e-06,	3.730648052468e+00,	6.260108089674e-06,	2.877585165341e+00,	8.383773236340e+00,	3.044046617782e+02,
-300	,2.025001769011e+00,	8.465253445096e-06,	3.730383888449e+00,	6.735114021211e-06,	2.877692828730e+00,	1.192725847856e+01,	3.042833640696e+02,
-150	,2.025443580271e+00,	8.085534211391e-06,	3.729743446661e+00,	7.101666872440e-06,	2.877593513466e+00,	8.711079379932e+00,	3.040797679164e+02,
0	,2.025274019869e+00,	8.371245934477e-06,	3.729766659634e+00,	7.131420060828e-06,	2.877520339751e+00,	5.192869434281e+00,	3.041064291277e+02]


data = [0	,2.025388946481e+00,	7.440085150116e-06,	3.729604188400e+00,	6.210607809432e-06,	2.877496567441e+00,	3.327931702131e+00,	3.040544253604e+02,
150	,2.025182849490e+00,	8.012263108351e-06,	3.729802251643e+00,	6.508717145295e-06,	2.877492550566e+00,	2.896465111765e+00,	3.041261083158e+02,
300	,2.024925120878e+00,	8.682141662836e-06,	3.730079847554e+00,	6.945089268096e-06,	2.877502484216e+00,	3.876705144155e+00,	3.042226673523e+02,
150	,2.025114486003e+00,	7.839792110792e-06,	3.729884981865e+00,	5.917128310583e-06,	2.877499733934e+00,	3.631951555250e+00,	3.041538246713e+02,
0	,2.025360536327e+00,	8.319911480083e-06,	3.729608609425e+00,	6.837522522481e-06,	2.877484572876e+00,	1.748397370113e+00,	3.040590154292e+02,
-150	,2.025629721928e+00,	9.149872056586e-06,	3.729352297928e+00,	6.838524845775e-06,	2.877491009928e+00,	2.713006185771e+00,	3.039659402052e+02,
-300	,2.025963119646e+00,	7.119421153113e-06,	3.729041701274e+00,	7.471165989772e-06,	2.877502410460e+00,	3.870794649086e+00,	3.038522472054e+02,
-150	,2.025673327891e+00,	9.651317845750e-06,	3.729301973284e+00,	5.841164418956e-06,	2.877487650588e+00,	2.261560024479e+00,	3.039488269344e+02,
0	,2.025429149390e+00,	7.495463478802e-06,	3.729536905800e+00,	6.789331658227e-06,	2.877483027595e+00,	1.422648838696e+00,	3.040338179160e+02]
'''

xdata 	= np.zeros(len(data)/8)
f_msm 	= np.zeros(len(data)/8)
f_msm_u	= np.zeros(len(data)/8)
f_msp 	= np.zeros(len(data)/8)
f_msp_u = np.zeros(len(data)/8)
f_average = np.zeros(len(data)/8)
Bz = np.zeros(len(data)/8)
Bx = np.zeros(len(data)/8)

for i,j in enumerate(data):
	if i%8==0:
		xdata[i/8] = j
	if i%8==1:
		f_msm[(i-1)/8] = j
	if i%8==2:
		f_msm_u[(i-2)/8] = j
	if i%8==3:
		f_msp[(i-3)/8] = j
	if i%8==4:
		f_msp_u[(i-4)/8] = j
	if i%8==5:
		f_average[(i-5)/8] = j
	if i%8==6:
		Bx[(i-6)/8] = j
	if i%8==7:
		Bz[(i-7)/8] = j
print xdata

f_average_u = np.sqrt(f_msm_u**2 + f_msp_u**2)/2.

plt.figure(1)
plt.errorbar(xdata,(f_msm-2.02)*1e3, f_msm_u*1e3)
plt.title('f_msms in MHz + 2020')
plt.xlabel('magnet steps')

plt.figure(2)
plt.errorbar(xdata,(f_msp-3.72)*1e3, f_msp_u*1e3)
plt.title('f_msmp in MHz + 3720')
plt.xlabel('magnet steps')

plt.figure(3)
plt.errorbar(xdata,(f_average-2.877)*1e6,f_average_u*1e6)
plt.xlabel('magnet steps')
plt.title('f_average in KHz (-2.877 GHz)')
estimated_ZFS = params.cfg['samples']['Hans_sil1']['zero_field_splitting']
plt.plot(np.array([min(xdata),max(xdata)]),np.array([(estimated_ZFS-2.877e9)*1e-3,(estimated_ZFS-2.877e9)*1e-3]) )


plt.figure(4)
plt.plot(xdata,Bz)
plt.xlabel('magnet steps')
plt.title('Bz')

plt.figure(5)
plt.plot(xdata,Bx)
plt.title('Bx')
plt.xlabel('magnet steps')













































