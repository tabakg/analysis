import numpy as np
from numpy import *
from scipy import optimize
# import pylab

# taken from the scipy fitting cookbook:
class Parameter:
    def __init__(self, value, name=''):
        self.value = value
        self.name = name

    def set(self, value):
        self.value = value

    def __call__(self):
        return self.value

###############################################################################
# fitting a 1d function
################################################################################

# TODO 
# - fitmethods should be classes
# - fit should actually also be a class, and we want a simple function as
# wrapper for interactive work; then we still need sth better for fixing,
# though; good maybe: generally identify parameters by names
def fit1d(x, y, fitmethod, *arg, **kw):
    """
    example: from analysis.lib.fitting import fit,common
             x=np.array([0,1,2,3,4])
             y=np.array([2,12,22,32,42])
             fit_result=fit_result=fit.fit1d(x,y,common.fit_line,2,8,ret=True,
                    fixed=[0],do_print=True)
             
    
    """
    
    # process known kws
    do_print = kw.pop('do_print', False)
    ret = kw.pop('ret', False)
    fixed = kw.pop('fixed', [])

    # use the standardized fitmethod: any arg is treated as initial guess
    if fitmethod != None:
        p0, fitfunc, fitfunc_str = fitmethod(*arg)
    else:
        p0 = kw.pop('p0')
        fitfunc = kw.pop('fitfunc')
        fitfunc_str = kw.pop('fitfunc_str', '')        
    
    # general ability to fix parameters
    fixedp = []
    for i,p in enumerate(p0):
        if i in fixed:
            fixedp.append(p)
    for p in fixedp:
        p0.remove(p)
   
    # convenient fitting method with parameters; see scipy cookbook for details
    def f(params):
        i = 0
        for p in p0:
            p.set(params[i])
            i += 1
        return y - fitfunc(x)

    if x is None: x = arange(y.shape[0])
    p = [param() for param in p0]
    
    # do the fit and process
    p1, cov, info, mesg, success = optimize.leastsq(f, p, full_output=True)
    if not success or cov == None: # FIXME: find a better solution!!!
        return False

    # package the result neatly
    result = result_dict(p1, cov, info, mesg, success, x, y, p0, 
            fitfunc, fitfunc_str)

    if do_print:
        print_fit_result(result)

    if ret:
        return result       

    return


###############################################################################
# tools, for formatting, printing, etc.
###############################################################################

# put all the fit results into a dictionary, calculate some more practical 
# numbers
def result_dict(p1, cov, info, mesg, success, x, y, p0, fitfunc, fitfunc_str):
    chisq = sum(info['fvec']*info['fvec'])
    dof = len(y)-len(p0)
    error_dict = {}
    error_list = []
    params_dict = {}
    
    # print cov, success, mesg, info
    for i,pmin in enumerate(p1):
        error_dict[p0[i].name] = sqrt(cov[i,i])*sqrt(chisq/dof)
        error_list.append(sqrt(cov[i,i])*sqrt(chisq/dof))
        params_dict[p0[i].name] = pmin

    result = {
        'success' : success,
        'params' : p1,
        'params_dict' : params_dict,
        'chisq': chisq,
        'dof': dof,
        'residuals_rms': sqrt(chisq/dof),
        'reduced_chisq': chisq/dof,
        'error' : error_list,
        'error_dict' : error_dict, 
        'cov' : cov,
        'p0' : p0,
        'fitfunc' : fitfunc,
        'fitfunc_str' : fitfunc_str,
        'x' : x,
        'y' : y,
        }
    
    return result

# convenient for pylab usage (or other interactive)
def do_fit_func(fitfunc, p0, y, x):
    result = _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))
    print_fit_result(result)
    return result

# make a string that contains the fit params in a neat format
def str_fit_params(result):
    
    # uncertainties are calculated as per gnuplot, "fixing" the result
    # for non unit values of the reduced chisq.
    # values at min match gnuplot
    
    str = "fitted parameters at minimum, with 68% C.I.:\n"
    for i,pmin in enumerate(result['params']):
        str += "%2i %-10s %12f +/- %10f\n" % \
            (i, result['p0'][i].name, pmin, result['error'][i])
    return str

def str_correlation_matrix(result):
    str = "correlation matrix:\n"
    str += "               "
    for i in range(len(result['p0'])): 
        str+= "%-10s" % (result['p0'][i].name,)
    str += "\n"
    
    for i in range(len(result['params'])):
        str += "%10s" % result['p0'][i].name
        for j in range(i+1):
            str+= "%10f" % \
                (result['cov'][i,j] / \
                     sqrt(result['cov'][i,i] * result['cov'][j,j]),)
        str+='\n'

    return str
    
def print_fit_result(result):
    if result == False:
       print "Could not fit data" 
    
    print "Converged with chi squared ", result['chisq']
    print "degrees of freedom, dof ", result['dof']
    print "RMS of residuals (i.e. sqrt(chisq/dof)) ", \
        sqrt(result['chisq']/result['dof'])
    print "Reduced chisq (i.e. variance of residuals) ", \
        result['chisq']/result['dof']
    print

    print str_fit_params(result)
    print str_correlation_matrix(result) 
    
