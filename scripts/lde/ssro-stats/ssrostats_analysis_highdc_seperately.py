import os, sys, time
import pickle
import pprint
import numpy as np
from matplotlib import pyplot as plt
from analysis import config

config.outputdir = r'/Users/wp/Documents/TUD/LDE/analysis/output'
config.datadir = r'/Volumes/MURDERHORN/TUD/LDE/analysis/data/ssro-stats'


class SSROStatAnalysis:

    def __init__(self):
        self.srcfolder = config.datadir
        self.savedir = os.path.join(config.outputdir, time.strftime('%Y%m%d')+'-ssro-stats')
        self.fname0 = 'ADwin_SSRO-000_fid_vs_ROtime.npz'
        self.fname1 = 'ADwin_SSRO-001_fid_vs_ROtime.npz'
        self.lt1suffix = 'LT1'
        self.lt2suffix = 'LT2'

        self.fid = {
                'LT1' : {
                    0 : [],
                    1 : [],
                    },
                'LT2' : {
                    0 : [],
                    1 : [],
                    },
                'LT2_highdc' : {
                    0 : [],
                    1 : [],
                    },
                }

        self.fiderr = {
                'LT1' : {
                    0 : [],
                    1 : [],
                    },
                'LT2' : {
                    0 : [],
                    1 : [],
                    },
                'LT2_highdc' : {
                    0 : [],
                    1 : [],
                    },
                }

        self.pathinfo = {
                'LT1' : [],
                'LT2' : [],
                'LT2_highdc' : [],
                }

        self.lt1idx = 14
        self.lt2idx = 25

    def load_data(self):
        
        print 'start reading data'

        for (path,dirs,files) in os.walk(self.srcfolder):
            for fn in files:
                if fn == self.fname0 or fn == self.fname1:
                    d = np.load(os.path.join(path, fn))
                    fid = d['fid']
                    fiderr = d['fid_error']
                    d.close()

                    b,folder = os.path.split(path)
                    timestamp = folder[:4]
                    b,date = os.path.split(b)[-4:]

                    
                    if path[-3:] == self.lt1suffix:
                        setup = 'LT1'
                    elif 'ssro_normal' in path:
                        setup = 'LT2'
                    else:
                        setup = 'LT2_highdc'
                                      
                    if fn == self.fname0 and setup == 'LT2_highdc':
                        setup = 'LT2'

                    state = 0 if fn == self.fname0 else 1
                    idx = self.lt1idx if path[-3:] == self.lt1suffix else self.lt2idx

                    self.fid[setup][state].append(fid[idx])
                    self.fiderr[setup][state].append(fiderr[idx])
                    
                    if fn == self.fname0:
                        self.pathinfo[setup].append(date+'/'+timestamp)

    def stats(self):
        
        self.meanfid = {
                'LT1' : {
                    0 : 0.,
                    1 : 0.,
                    },
                'LT2' : {
                    0 : 0.,
                    1 : 0.,
                    },
                'LT2_highdc' : {
                    0 : 0.,
                    1 : 0.,
                    },
                }

        self.fidstdev = {
                'LT1' : {
                    0 : 0.,
                    1 : 0.,
                    },
                'LT2' : {
                    0 : 0.,
                    1 : 0.,
                    },
                'LT2_highdc' : {
                    0 : 0.,
                    1 : 0.,
                    },
                }

        for setup in self.fid:
            for state in self.fid[setup]:
                print setup, state
                print 'mean = %.4f' % np.mean(np.array(self.fid[setup][state]))
                print 'statistical uncertainty = %.4f' % \
                        np.std(np.array(self.fid[setup][state]))
                print ''

                self.meanfid[setup][state] = np.mean(np.array(self.fid[setup][state]))
                self.fidstdev[setup][state] = np.std(np.array(self.fid[setup][state]))
                

        fig = plt.figure(figsize=(10,10))
        
        for i, setup, state in zip(range(1,5), ['LT1', 'LT1', 'LT2', 'LT2'], [0,1,0,1]):

            ax = plt.subplot(2,2,i)
            ax.hist(self.fid[setup][state], color='k', histtype='step', hatch='/')           
            if i==4:
                ax.hist(self.fid['LT2_highdc'][1], color='r', histtype='step', hatch='//')

            ax.set_title(setup + ', ms = ' + str(state))
            plt.text(ax.get_xlim()[0]+0.0004,4.,'%.4f +/- %.4f' % \
                    (self.meanfid[setup][state], self.fidstdev[setup][state]),
                    backgroundcolor='w')

            if i==4:
                plt.text(ax.get_xlim()[0]+0.0004,5.,'%.4f +/- %.4f' % \
                        (self.meanfid['LT2_highdc'][1], self.fidstdev['LT2_highdc'][1]),
                        color='r', backgroundcolor='w')
            
            ax.locator_params(nbins=4)
            ax.set_xlabel('Fidelity')
            ax.set_ylabel('Occurrences')

        plt.tight_layout()

        # fig = plt.figure(figsize=(10,10))

        # for i, setup, state in zip(range(1,5), ['LT1', 'LT1', 'LT2', 'LT2'], [0,1,0,1]):

        #     ax = plt.subplot(2,2,i)
        #     ax.errorbar(np.arange(len(self.fid[setup][state])), np.array(self.fid[setup][state]),
        #             yerr=np.array(self.fiderr[setup][state]), fmt='ko')
        #     ax.axhline(y=self.meanfid[setup][state], ls=':')
        #     ax.set_title(setup + ', ms = ' + str(state))
        #     ax.set_xticks(np.arange(len(self.fid[setup][state])))
        #     ax.set_xticklabels(self.pathinfo[setup])
        #     labels = ax.get_xticklabels()
        #     plt.setp(labels, rotation=90)

        #     ax.set_ylabel('Fidelity')
        #     ax.set_xlabel('Run')

        # plt.tight_layout()


if __name__ == '__main__':
    a = SSROStatAnalysis()
    a.load_data()
    a.stats()

    if not os.path.exists(a.savedir):
        os.makedirs(a.savedir)

    f = open(os.path.join(a.savedir, 'fidelities.pkl'), 'wb')
    pickle.dump(a.meanfid, f)
    f.close()

    f = open(os.path.join(a.savedir, 'stdevs.pkl'), 'wb')
    pickle.dump(a.fidstdev, f)
    f.close()


