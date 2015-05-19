# Don Willcox
# Last Modified: March 6, 2015

from collections import OrderedDict
import numpy as np
from PermParams import PermParams

# batch-prepares new Mesa inlists given a template file and a set of parameters and values
templatefile = 'inlist_1.0'

# Create a rule
r = OrderedDict([])
r['Reimers_wind_eta']=np.linspace(0.0,2.0,5) # These could be regular python lists or numpy 1-d arrays
r['Blocker_wind_eta']=np.linspace(0.0,2.0,5)

# Identify the parameter data types
partypes = OrderedDict([])
partypes['Reimers_wind_eta'] = 'float'
partypes['Blocker_wind_eta'] = 'float'

# Print rule to console
for k in r.keys():
        print '-------------------------'
        print 'Parameter: ' + k
        print r[k]

# Generate a set of inlists
pmi = PermParams('mesa')
pmi.writerules(r=r,partypes=partypes,tpath=templatefile,
               exec_t_dir='/home/dwillcox/simulations/mesa_runs/uncertainties/1M_pre_ms_to_wd',
               dir_prefix='pmswd')

        
