# This class implements functions for reading parameter files
# and modifying their contents according to a set of rules,
# generating combinations of those rules if need be. It also
# does all the file copying for setting up directories with executables.
# It has not been tested on Windows. While python is pretty 
# portable, it is always possible some of the file copying stuff 
# might not work properly on Windows.

# Don Willcox
# Last Modified: May 18, 2015

from collections import OrderedDict
import re
import os, shutil

class PermParams:
        def __init__(self,code_name=None):
                """
                Define some class variables.
                """
                self.lstemp = []
                self.exec_t_dir = None # Template Directory for the executable and its files
                self.dir_prefix = None # Prefix for the rule directories
                self.tname = None # Name of the template parameter file
		self.tdir = None # Directory of the template parameter file
		
		self.code_specifics = {}
		cs_flash = {'comment':'#', 'exp':'e'}
		cs_mesa = {'comment':'!', 'exp':'d'}
		self.code_specifics['flash'] = cs_flash
		self.code_specifics['mesa'] = cs_mesa

		if (not code_name) or not (code_name.lower() in self.code_specifics.keys()):
				print 'Please supply a valid code name. Options are: '
				for cn in self.code_specifics.keys():
					print cn
				exit()
		else:
			self.code_name = code_name

                # Rule Permutation NUMber: a dictionary keyed by the 
                # combination number where the value is a dictionary 
                # keyed by parameter name with value permuted parameter value.
                self.rpnum = OrderedDict([])
                self.cfname = OrderedDict([])

                # Dictionary to hold parameter types
                self.ptypes = OrderedDict([])

        def sdec(self,x):
                """
                Format the float x as a scientific notation string with 14 digits after the decimal and 'd' marking the exponent.
                """
                s='{:1.14e}'.format(x)
                return s.replace('e',self.code_specifics[self.code_name]['exp'])

        def permx(self,x,y=None,ntot=None):
                """
                This generator is an iterable which returns unique 
                permutations picking 1 element from each of the lists
                in x. It is equivalent to for loops nested at 
                depth len(x) such that the top level loop scans 
                over the elements of x[0] and the deepest level loop 
                scans the elements of x[-1].

                When calling permx, pass one argument into x: a list of lists.
                The arguments y and ntot permit permx to call 
                itself and remember the list y containing the current permutation
                and the integer ntot which is the length of list x.
                """
                if y==None:
                        y = ['' for xi in x]
                if ntot==None:
                        ntot = len(x) 

                pos = ntot-len(x) 

                for xi in x[0]:
                        y[pos] = xi
                        if (pos==ntot-1):
                                yield y
                        else:
                                # Iterate over the remaining elements of x
                                for p in self.permx(x[1:],y,ntot):
                                        yield y

        def gettemplate(self):
                """
                Read the lines from the template file into the list lstemp
                """
		fromdir = os.getcwd()
		os.chdir(self.tdir)
                ftemp = open(self.tname,'r')
                self.lstemp = []
                for l in ftemp:
                        self.lstemp.append(l)
                ftemp.close()
		os.chdir(fromdir)
        
        def preprules(self,r): 
                """
                This function takes the following arguments:
                r: a dictionary (ideally an OrderedDictionary) with parameter names as keys and lists of parameter values as values r[k]
                partypes: a dictionary with parameter names as keys and values of 'string', 'float', or 'int' identifying r[k] elements
                tname: a string containing the prefix for a logfile name. The name is composed by [tname].log. tname must also match
                the name of the template inlist file.

                Next, writerules reads the template inlist by calling self.gettemplate then calls self.permx to 
                generate all unique combinations of the parameter values and uses regular expressions to insert
                these values in the template, writing files named [tname]_c[cnum], where cnum is the combination number.

                The logfile generated identifies the combination numbers cnum with the parameters and values used.
                """
                self.rpnum = OrderedDict([])
                klist = r.keys()
                rvals = [r[k] for k in klist] # list of lists, indices follow key order, rvals[i] is r[k]
                cnum = 0
                for rp in self.permx(rvals):
                        cnum += 1

                        # rp[i] contains the permuted element of r[klist[i]]
                        self.rpnum[cnum] = dict([(klist[i],rp[i]) for i in range(0,len(klist))])

        def mkruledirs(self):
                dirpre = 'rule_permutations'
                if self.dir_prefix != None:
                        dirpre = self.dir_prefix
                here = os.getcwd()
                putdir = os.path.join(here,dirpre)
                if self.exec_t_dir == None:
                        # No template executable directory supplied
                        os.mkdir(putdir)
		# Determine if we need to make separate rule subdirectories, avoid if only 1 rule
		if len(self.rpnum.keys())==1:
			single_key = True
		else:
			single_key = False
                for cnum in self.rpnum.keys():
			if single_key:
				if self.exec_t_dir != None:
		                        shutil.copytree(self.exec_t_dir,putdir,symlinks=True)
				# Move the permuted template parameter file to the destination directory
	                        shutil.move(os.path.join(here,self.cfname[cnum]),os.path.join(putdir,self.tname))
			else:
	                        dirname = 'c' + str(cnum)
	                        cdir = os.path.join(putdir,dirname)
	                        if self.exec_t_dir == None:
	                                os.mkdir(cdir)
	                        else:
	                                # Copy the template executable directory
	                                shutil.copytree(self.exec_t_dir,cdir,symlinks=True)
				# Move the permuted template parameter file to the executable directory
	                        shutil.move(os.path.join(here,self.cfname[cnum]),os.path.join(cdir,self.tname))
                       
        def writerules(self,r=None,partypes=None,tpath=None,exec_t_dir=None,dir_prefix=None):
		"""
		This function writes the rule permutations to individual parameter files and then calls 
		mkruledirs to move the parameter files into executable directories.
		This is likely the only function which needs to be modified if you want to work
		with a parameter file for a code other than MESA, so long as there is only one parameter file.

		For simple modifications, like changing the comment symbol or specifying whether to use e or d to
		denote the scientific notation exponent, you should keep this function code-agnostic by
		accomodating these changes via the self.code_specifics dictionary just as is done for FLASH.

		For more complex modifications, I would suggest making a new class.
		"""
                # call gettemplate and preprules if necessary
                if tpath != None:
			tpathsp = tpath.split(os.sep)
			self.tname = tpathsp[-1]
			if (len(tpathsp)==1):
				self.tdir = os.getcwd()
			else:
				self.tdir = tpath[:-len(self.tname)]
                        self.gettemplate()
                if r != None:
                        self.preprules(r)
                if partypes != None:
                        self.partypes = partypes
                if exec_t_dir != None:
                        self.exec_t_dir = exec_t_dir
                if dir_prefix != None:
                        self.dir_prefix = dir_prefix
                self.cfname = OrderedDict([])

		comment_char = self.code_specifics[self.code_name]['comment']

		# Write permuted parameter files.
                flog = open(self.tname + '.log','w')
                for cnum,rpd in self.rpnum.iteritems():
                        klist = rpd.keys()

                        # open an output file for this rule rnum and combination cnum
                        self.cfname[cnum] = self.tname + '_c' + str(cnum)
                        frc = open(self.cfname[cnum],'w')

                        # write this rule and combination to the log
                        flog.write('-------------------------------\n')
                        flog.write('comb: ' + str(cnum) + '\n')
                        for k in klist:
                                if self.partypes[k]=='float':
                                        flog.write(k + ': ' + self.sdec(rpd[k]) + '\n')	
                                else:
                                        flog.write(k + ': ' + str(rpd[k]) + '\n')

                        # Create and log this inlist permutation
                        for l in self.lstemp:
                                # check to see if line l contains any of the keys in klist. 
                                # If so, replace the value with that key's value in rp for this permutation.
                                pcline = re.compile('\s*'+comment_char) # Line is commented
                                if (pcline.match(l)):
                                        frc.write(l) # Write the unmodified line
                                        continue
                                hask = False
                                for k in klist:
                                        pk = re.compile('\s*'+k+'\s*=\s*')
                                        mk = pk.match(l)
                                        if mk: # Key k is a match to line l
                                                # see if this line has a trailing comment and preserve it
                                                pcomm = re.compile(comment_char+'.*')
                                                mcomm = pcomm.search(l)
                                                comment = ''
                                                if mcomm:
                                                        # There is a trailing comment, keep it
                                                        comment = l[mcomm.start():]
                                                lnew = l[0:mk.end()]
                                                # test if rpd[k] is a float, if so put in a d0, otherwise don't
                                                if self.partypes[k]=='float':
                                                        srp = self.sdec(rpd[k])
                                                        lnew += srp + ' ' + comment 
                                                else:
                                                        lnew += str(rpd[k]) + ' ' + comment 
                                                frc.write(lnew + '\n')
                                                hask = True
                                                break
                                # Line matched no keys in klist
                                if not hask:
                                        frc.write(l) # Write the unmodified line
                        frc.close()
                flog.close()
                self.mkruledirs()
				
						
