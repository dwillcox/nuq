# Don Willcox
# Last Modified: May 18, 2015

from collections import OrderedDict
import numpy as np
from PermParams import PermParams
import os

# batch-prepares new FLASH parameter files given a template file and a set of parameters and values
template_root = '/home/dwillcox/codes/astro/PermuteParameters/Brendan_Realizations/D20_T7_Xfiducial'
template_dir_base = 'Realization_'
template_file = 'flash.par'

dest_root = '/home/dwillcox/codes/astro/PermuteParameters/scratch/execs'

for i in xrange(1,31):
	snum = '{0:>03}'.format(i)
	template_dir = template_dir_base + snum
	template_file_path = template_root + os.sep + template_dir + os.sep + template_file

	# Create a rule
	r = OrderedDict([])
	r['basenm'] = ['"400k_Tc7e8_co_wd_R'+snum+'_"']
	r['initialWDFile'] = ['"400k_Tc7e8_cf-Brendan_flash.dat"']

	# Identify the parameter data types
	partypes = OrderedDict([])
	partypes['basenm'] = 'string'
	partypes['initialWDFile'] = 'string'

	# Generate a set of inlists
	pmi = PermParams('flash')
	pmi.writerules(r=r,partypes=partypes,tpath=template_file_path,
        	       exec_t_dir='/home/dwillcox/codes/astro/PermuteParameters/flashtemplate',
	               dir_prefix=template_dir)

        
