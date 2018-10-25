#coding=utf-8
import fuzzy.storage.fcl.Reader
import fuzzy.Adjective
import fuzzy.doc.structure.dot.dot as fd
import fuzzy.operator.Compound 
import warnings
from  copy import deepcopy
import sys
from pylab import *
from pydot import *
import matplotlib.cm as cmx
from pydot import * 
from matplotlib.path import Path
import matplotlib.patches as patches
import os
import tempfile

""" Custom functions for the custom update of states """
def fun1(time): return 0.0
def fun2(time): return 1.0


class FuzzySystem(object):


	"""FuzzySystem Class: loads the FCL file"""
	def __init__(self, input_file="", dump=False, max_time=1.0):
		super(FuzzySystem, self).__init__()
		if input_file=="":
			print "ERROR: please specify a FCL file"
			exit(-1)
		#file = open(input_file, 'r')
		#print file.read()

		
		self.fuzzySystem = fuzzy.storage.fcl.Reader.Reader().load_from_file(input_file)	
		print " * FCL", input_file, "correctly loaded, system initialized"
		#f.close()
		if dump: self.print_info()
		self.iteration = 0
		self.observed_elements = {}
		self.all_elements = []
		self.whole_dynamics = {}
		self.whole_memberships = {}
		self.list_observed_elements = []
		self.graph = None
		self.maximum_time = max_time
		self.simulation_time = 0.0
		self.simulation_iterations = 0
		self.updaters = None
		self.state = {}


	""" 
		Creates the empty lists for the observations of the states.
	"""
	def create_observers(self, list_obs):
		for elemento in list_obs:
			self.observed_elements[elemento] = []
		self.list_observed_elements = list_obs
		print " * Will save dynamics for", list_obs


	"""
		We organize the observed states into subgroups.
	"""
	def create_groups_observed(self, liste):
		self.lists_observed = liste
		flatten = [item for sublist in liste for item in sublist]
		self.create_observers(flatten)
		
	"""
		Plot and save to files the observed groups of states.
	"""
	def plot_observed_to_files(self, prefix):
		folder=  os.path.dirname(prefix)
		try:
			os.makedirs(folder)
		except:
			print "WARNING: unable to create the output folder", folder
			
		for n, group in enumerate(self.lists_observed):
			print " Showing", group			
			figure()
			self.subroutine_plot(group)
			savefig(prefix+"fig"+str(n)+".png")
		# show()

	"""
		Plot the observed groups of states.
	"""
	def plot_observed(self):
		for group in self.lists_observed:
			print " Showing", group			
			figure()
			self.subroutine_plot(group)
		show()

	
	"""
		Actual plot code.
	"""
	def subroutine_plot(self, group):
		values = range(len(group))
		jet = cm = plt.get_cmap('jet') 
		cNorm  = Normalize(vmin=0, vmax=values[-1])
		scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

		xax = linspace(0, self.maximum_time, self.simulation_iterations)
		for numtest, variabile in enumerate(group):
			colorVal = scalarMap.to_rgba(values[numtest])
			# plot(xax,self.observed_elements[variabile], "o-", label=variabile, color= colorVal, marker=markers[numtest])
			plot(xax,self.observed_elements[variabile], "o-", label=variabile, color= colorVal, marker=self.dict_markers[variable])
		legend(prop={'size': 8.5}, loc='best')
		ylabel("Level [a.u.]")
		xlabel("Time [a.u.]")


	"""
		Saves the observations to an output file. 
	"""
	def write_observed_to_file(self, path=None):
		if path==None:		
			raise Exception("please specify an output file")			
		head = "#"+"\t".join(self.observed_elements.keys())+"\n"
		OUT = []
		xax = linspace(0, self.maximum_time, self.simulation_iterations)
		OUT.append( xax )
		for vals in self.observed_elements.values():			
			OUT.append(vals)	
		OUT = array(OUT).T
		savetxt(path, OUT, header=head, delimiter="\t")

	
	"""Prints debug information"""
	def print_info(self):
		print " * Dumping information about Cell Death Fuzzy System."

		print "   List of variables:"
		for i in self.fuzzySystem.variables:
			print "    ", i

		print "   List of rules:"
		for r in self.fuzzySystem.rules:
			print "    ", r


	def remap(self, state):
		ret = {}
		for key in state:
			if key!="Time":
				ret[key+"OUT"] = state[key]
		return ret

	def countermap(self, state, time):
		ret = {}
		for key in state:
			ret[key[:-3]] = state[key]
		ret['Time']=time
		return ret


	def update_custom_states(self, time, my_input, verbose=False):

		import inspect

		if verbose: print " * Applying", len(self.updaters),"automatic updaters"
		
		if verbose: 			
			for n,f,i in self.updaters:
				print "   ", i, n, inspect.getsource(f).strip("\n")

		# we must know which node to perturb, how (fun) and in which time window to apply the perturbation
		for (node, fun, intervals) in self.updaters:						
			
			# if this is not the right moment, do not overwrite the state
			update = False
			if len(intervals)>0:
				#for begin, end in intervals:
					# if time>begin and time<end:
				if self.is_time_in_intervals(time, intervals):
					update = True
					if verbose: print " * Using custom update on", node, "at time", time, "which is contained in intervals", intervals
					#break
			else:
				if verbose: print " * Using custom update on", node, "at time", time
				update = True

			if not update: 
				if verbose: print " * NOT updating", node, "at time", time
				continue
			else:
				my_input[node] = fun(time)
				if verbose: print " * Updated", node, "with value", fun(time)


	def set_state_updaters(self, updaters, verbose=False):
		for up in updaters:	
			try:
				up[2]
			except:
				up.append([[0,self.maximum_time]])
		self.updaters = updaters
		if verbose:
			for up in updaters:
				 print up[0], up[1](1), up[2]


	def calculate_time(self, iteration, iterations, verbose=False):
		if iterations==1: return 0.
		return self.maximum_time*float(iteration)/(iterations-1)


	def return_all_output_variable_names(self):
		ret = {}
		for name, i in self.fuzzySystem.variables.items():
			if isinstance(i , fuzzy.OutputVariable.OutputVariable):
				ret[str(name)]=[0, 0]
		return ret


	def get_singleton_value(self, adj):
		return adj.set.getCOG()

	def process_operators(self, operator, verbose=False, suppresswarning=True):
		if isinstance(operator, fuzzy.operator.Input.Input):
			if verbose: print "    Simple input", operator.adjective.getName(self.fuzzySystem), 
			MEMB = operator.adjective.membership
			if verbose: print "membership =", MEMB
			if MEMB==None:
				if not suppresswarning:
					warnings.warn("input for "+operator.adjective.getName(self.fuzzySystem)[1]+" not specified")
			return MEMB
			
		elif isinstance(operator, fuzzy.operator.Compound.Compound):
			if verbose: print "    Multiple inputs: "			
			BEST = sys.float_info.max
			for inp in operator.inputs:
				MEMB = self.process_operators(inp, verbose=verbose)
				if MEMB==None: 
					if not suppresswarning:
						warnings.warn("input for "+inp.adjective.getName(self.fuzzySystem)[1]+" not specified")
				elif MEMB<BEST:
					BEST = MEMB			
			return BEST
				# MEMB = inp.adjective.membership
				# print "    ", inp.adjective.getName(self.fuzzySystem), "membership =", MEMB
						

	def actual_sugeno_inference(self, verbose=False):

		all_outputs = self.return_all_output_variable_names()		

		for name, rule in self.fuzzySystem.rules.items():
			if verbose: print " * Processing rule", name

			MEMB = 0
			DENO = 0
			NUME = 0

			SINGLETON = 0


			if isinstance(rule.adjective, fuzzy.Adjective.Adjective):
				if verbose: print "WARNING: Aggettivo output semplice, non supportato"
				pass
			elif isinstance(rule.adjective,list):
				
				if verbose: print "  * Processing list of OUTPUT adjectives..."

				# what output are we updating?
				for adj in rule.adjective:
					outlabel, outname = adj.getName(self.fuzzySystem)
					
					if verbose: print "   ", outlabel, outname, 
					SINGLETON = self.get_singleton_value(adj)
					if verbose: print "whose singleton is", SINGLETON

				# process operators (i.e., input nodes)
				MEMB = self.process_operators(rule.operator, verbose=verbose)
				if MEMB==None:
					# raise Exception("error: input for "+inp.adjective.getName(self.fuzzySystem)[1]+" not specified")
					# warnings.warn("input for "+inp.adjective.getName(self.fuzzySystem)[1]+" not specified")
					if verbose: print "WARNING: cannot calculate MAX membership value"
					pass
				else:
					DENO += MEMB	
					NUME += MEMB*SINGLETON
					if verbose: print "      Product =", MEMB*SINGLETON

			else:
				raise Exception("rule target not set.")

			all_outputs[outname][0]+=NUME
			all_outputs[outname][1]+=DENO

		if verbose: print all_outputs

		final = {}
		for out, valout in all_outputs.items():
			if valout[1]==0:
				final[out]=0
			else:
				final[out] = valout[0]/valout[1]
		return final

	def sugeno_inference(self, my_input, verbose=False):
		"""
			Calculates the Sugeno rule of inference using the specified
			input values and updating the specified output values.
			Appearently, the Sugeno method is not implemented in pyfuzzy. 
			This method replaces pyfuzzy's calculate() method.
		"""

		self.fuzzySystem.reset()
		self.fuzzySystem.fuzzify(my_input)
		
		# the following replaces pyfuzzy's inference() method
		# my_output = self.actual_sugeno_inference(verbose=verbose)
		my_output = self.actual_sugeno_inference(verbose=False)

		# self.fuzzySystem.defuzzify(my_output)
		return my_output


	def is_time_in_intervals(self, time, intervals):
		#print time, intervals
		if len(intervals)==0:
			return True
		for begin, end in intervals:
			if time>=begin and time<=end:
				return True
		return False


	def update_states(self, time=0, store_everything=False, verbose=True, Sugeno=False, dump_to_file="debug.txt"):
		
		if verbose: print " * Time", time

		if time==0 and dump_to_file!="":
			with open(dump_to_file, "w") as fo:
				fo.write("# debug output dump\n\n")
		
		my_input = deepcopy(self.state)		
		my_input['Time']=time
		my_output = self.remap(my_input)

		self.update_custom_states(time, my_input, verbose=verbose)

		list_automatic = {}
		for (k,v,w) in self.updaters:
			if self.is_time_in_intervals(time, w): 
				list_automatic[k]=v

		if dump_to_file!="":
			with open(dump_to_file, "a") as fo:
				fo.write("TIME: "+str(time)+"\n\n")
				fo.write("AUTOMATIC UPDATERS:\n")
				for v,k in list_automatic.items():
					fo.write(v+"\t"+str(k(time))+"\n")
				fo.write("\n\n")

		if store_everything:
			for variabile in self.all_elements:
				if variabile in list_automatic:
					val =  list_automatic[variabile](time)					
					self.whole_dynamics[variabile].append(val)						
				else:				
					valore = self.state[variabile]
					self.whole_dynamics[variabile].append(valore)					

		###############################################################################
		############################### SIMULATION STEP ###############################
		###############################################################################
		if verbose: print " * State of the fuzzy system before Sugeno inference:", my_input
		if not Sugeno: 	self.fuzzySystem.calculate(my_input, my_output)			
		else:			my_output = self.sugeno_inference(my_input, verbose=verbose)			
		if verbose: print " * State of the fuzzy system after Sugeno inference: ", my_output
		###############################################################################
		############################### SIMULATION STEP ###############################
		###############################################################################
		
		# remove the postfixes (e.g., "out") from variable names 
		self.state = self.countermap(my_output, my_input['Time'])

		# save states for observed elements
		for variabile in self.observed_elements:
			if variabile in self.state:
				valore = self.state[variabile]
				self.observed_elements[variabile].append(valore)
			else:				
				for n,f in self.updaters:
					if n==variabile:
						val = f(time)
						self.observed_elements[n].append(val)
	
		if store_everything:
			for variabile in self.all_elements:
				self.whole_memberships[variabile].append(self.get_membership(variabile))
				

	def associate_colors_to_species(self, color_map='jet'):
		values = range(len(self.all_elements))
		cm = plt.get_cmap(color_map)
		if len(self.all_elements) > 0:
			cNorm  = Normalize(vmin=0, vmax=values[-1])
			scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
			self.dict_colors={}
			for numtest, variabile in enumerate(self.all_elements):
				self.dict_colors[variabile]=scalarMap.to_rgba(values[numtest])


	def associate_markers_to_species(self):
		markers=[]
		for m in Line2D.markers:
		    try:
		        if len(m) == 1 and m != ' ':
		            markers.append(m)
		    except TypeError:
		        pass

		self.dict_markers = {}
		for n,el in enumerate(self.all_elements):
			self.dict_markers[el]=markers[n%len(markers)]

	def simulate(self, iterations=0, store_everything=False, verbose=False, Sugeno=False, dump_to_file=""):

		if verbose:
			print " * Simulation started"
			if Sugeno: print " * Simulating with SUGENO"

		# create storage dictionary
		self.all_elements = self.get_list_input_variables()

		# experimental
		self.associate_markers_to_species()
		self.associate_colors_to_species()

		if store_everything:			
			for x in self.all_elements:				
				self.whole_dynamics[x]=[]
				self.whole_memberships[x]=[]
		else:
			for elemento in self.list_observed_elements:
				self.observed_elements[elemento] = []
		
		self.simulation_time = 0
		self.simulation_iterations = iterations

		for i in xrange(iterations):						
			if verbose: 
				print "-"*100
				print " * Simulation iteration", i
			self.iteration = i
			self.simulation_time = self.calculate_time(i, iterations, verbose=verbose)

			self.update_states(
				time=self.simulation_time,
			 	store_everything=store_everything, 
			 	verbose=verbose,
			 	Sugeno=Sugeno ,
			 	dump_to_file=dump_to_file
			 )
		
		print "-"*100
		print " *** Final state of the simulation ***"
		if store_everything:
			for k,v in self.whole_dynamics.items():
				print k, v[-1], "\t",		
		else:
			for k,v in self.observed_elements.items():
				print k, v[-1], "\t",
		print 
		return True


	def unpack_antecedents(self, operator):
		""" 
			Returns the antecedents or a list of compound antecedents.
			It is worth noting that the list can contain further lists.
		"""
		if isinstance(operator, fuzzy.operator.Compound.Compound):
			coll = []
			for inp in operator.inputs:
				coll.append(self.unpack_antecedents(inp))
			return coll
		else:
			op = operator.adjective.getName(self.fuzzySystem)
			what = op[1]
			how = op[0]
			return what+" IS "+how
			
	def antecedents_list_to_string(self, antlist):
		if isinstance(antlist, list):
			group = []
			for el in antlist:
				group.append(self.antecedents_list_to_string(el))
			return "(" + " AND ".join(group) +")"
		else:
			return antlist
		# output_string = "IF " + " AND ".join(antecedents) + " THEN "

	def unpack_consequents(self, operator):
		if isinstance(operator, list):
			coll = []
			for inp in operator:
				coll.append(self.unpack_consequents(inp))
			return coll
		else:
			op = operator.getName(self.fuzzySystem)
			what = op[1]
			how = op[0]
			return what+" IS "+how


	def rule_to_string(self, rule, verbose=False):
		"""
			Given a pyfuzzy rule, it reconstructs a string in the form
			IF this IS that THEN bla.
		"""
		if verbose: print " * Analyzing", rule[0]
		rule = rule[1]
		
		antecedents = self.unpack_antecedents(rule.operator)
		output_string = "IF " + self.antecedents_list_to_string(antecedents) +" THEN "
		consequents = self.unpack_consequents(rule.adjective)
		output_string += " AND ".join(consequents) 
		
		return output_string


	def get_list_rules(self):
		"""
            Creates and returns a dictionary of all rules, loaded from an FCL file and stored in the FuzzySystem.
            The list of rules is grouped according to the output.
        """
		rule_dictionary = {}
		for el in self.get_list_input_variables():
			rule_dictionary[el] = []
		for name, rule in self.fuzzySystem.rules.items():
			try:
				pos = name.find("_rules.")
				target = name[:pos]
				rule_dictionary[target].append((name,rule))
			except:
				warn("it was specified a rule on an inexistant element")
		return rule_dictionary

	
	#mio rimuove il il blocco delle regole di un nodo
	def deleteRulesNode(self, nodename):
		toRemove = []
		for key, value in self.fuzzySystem.rules.items():
			if nodename +'_rules' in key:
				toRemove.append(key)

		for i in toRemove:
			del self.fuzzySystem.rules[i]
    
    #mio rimuove le regole in cui compare il nodo
	def deleteRulesAntecedent(self, listAntecedents):
		for i in listAntecedents:
			value = i[0]
			del self.fuzzySystem.rules[value]

	
	def copyRules(self,nodename, newname):
		print #self.fuzzySystem.rules.items()
		dict_copy = {}
		i = 0
		for key, value in self.fuzzySystem.rules.items():
			if nodename + '_rules' in key:
				print 'da copy: ',key
				self.fuzzySystem.rules[unicode(newname+'_rules.' + str(i))] = value
				dict_copy[newname+'_rules.' + str(i)] = value
				i = i + 1
		print 'mio dizionario: ',dict_copy



		#self.fuzzySystem.rules[newname] = a

		    
			
				





	def draw_diagram(self, list_colors=None, list_clusters=None):
		self.graph = Dot(graph_type='digraph', strict=True, splines='ortho', pad ="0.2", overlap="False", nodesep="0.3", ranksep="0.5")
		# 1self.graph = Dot(graph_type='digraph', strict=True, splines='ortho', ranksep="0.5", nodesep="0.5", overlap="Scale")


		for name, rule in self.fuzzySystem.rules.items():
			for a in rule.adjective:
				target_name = a.getName(self.fuzzySystem)[1][:-3]
				if target_name in list_colors:
					target = Node(target_name, shape="rectangle", style="rounded, filled", 
						fillcolor=list_colors[target_name], width="1.5" )
				else:
					target = Node(target_name, shape="rectangle", style="rounded", width="1.5")
			
				try: 
					for i in xrange(1,len(rule.operator.adjective.getName(self.fuzzySystem)),2):
						source_name = rule.operator.adjective.getName(self.fuzzySystem)[i]
						if source_name in list_colors:
							source = Node(source_name, shape="rectangle", style="rounded, filled", 
								width="1.5", fillcolor=list_colors[source_name])
						else:
							source = Node(source_name, shape="rectangle", style="rounded", width="1.5", )
						self.graph.add_edge(Edge(source, target))
				except:
					# probably a compound
					for sources in rule.operator.inputs:
						src =  sources.adjective.getName(self.fuzzySystem)[1]
						source = Node(src, shape="rectangle", style="rounded", width="1.5" )
						self.graph.add_edge(Edge(source, target))

				self.graph.add_node(target)
				self.graph.add_node(source)

		for key, values in list_clusters.items():
			print " * Adding subgraph", key
			if key[0]=="*":
				name = key[1:]
				newcluster = Cluster(str(name)[0], label=str(name), style="invis")			
			else:
				name = key
				newcluster = Cluster(str(name)[0], label=str(name), style="dotted")			
			for v in values:
				newcluster.add_node(Node(str(v)))
			self.graph.add_subgraph(newcluster)
		
		self.graph.write_pdf("diagram.pdf")
		print " * Driagram drawn"

	def plot_all(self, path="dump_all"):
		print "Dumping everything in the System into file", path
		with open(path+".dot", "w") as fo:
			# fd.print_header(fo, self.fuzzySystem)
			fd.printDot(self.fuzzySystem, fo)
			# fd.print_footer(fo)
		graph  = graph_from_dot_file(path+".dot")
		graph.write_png(path+".png")

	def plot_variables(self, path="dump_variables"):
		print "Dumping all variables in the System into file", path
		with open(path+".dot", "w") as fo:
			fd.print_header(fo, self.fuzzySystem)
			fd.printVariablesDot(self.fuzzySystem, fo)
			fd.print_footer(fo)
		graph  = graph_from_dot_file(path+".dot")
		graph.write_png(path+".png")

	def plot_rules(self, path="dump_rules"):
		print "Dumping all rules in the System into file", path
		with open(path+".dot", "w") as fo:
			fd.print_header(fo, self.fuzzySystem)
			fd.printRulesDot(self.fuzzySystem, fo)
			fd.print_footer(fo)
		graph  = graph_from_dot_file(path+".dot")
		graph.write_png(path+".png")


	def determine_polygon(self, adjective="", attribute=""):
		for name, var in self.fuzzySystem.variables.items():
			if name==attribute: 
				for name2, var2 in var.adjectives.items():
					if name2==adjective:
						return var2.set.points
		raise Exception("cannot find adjective " + adjective + " for attribute " + attribute)			
		return None

	def determine_membership(self, adjective="", attribute="", dump=False):
		if dump: print "Starting attribution of", attribute, "=", adjective
		for name, var in self.fuzzySystem.variables.items():
			if name==attribute: 
				for name2, var2 in var.adjectives.items():
					if name2==adjective:
						if dump: print name, name2, var2.membership
						return var2.membership
		raise Exception("cannot find adjective " + adjective + " for attribute " + attribute)			
		return None

	def plot_polygon(self, verts=[], color="orange", clip=0.5, ax=None):

		# print clip
		
		quads = [ (0,clip), (0,0), (1,0), (1,clip), (0,0) ]
		#quads = [ (0,0), (0,.3), (1,.3), (1,0), (0,0) ]

		codes = [Path.MOVETO]
		for i in xrange(len(verts)-1):
			codes.append(Path.LINETO)
		codes.append(Path.CLOSEPOLY)
		verts.append((0,0))

		codes2 = [Path.MOVETO,
	         Path.LINETO,
	         Path.LINETO,
	         Path.LINETO,
	         Path.CLOSEPOLY,
	         ]

		path = Path(verts, codes)
		path2 = Path(quads, codes2)

		# patch = patches.PathPatch(path, facecolor=color, alpha=0.5,  lw=0)
		patch = patches.PathPatch(path, facecolor=color, alpha=0.75,  lw=0)
		patch2 = patches.PathPatch(path2, facecolor='none', edgecolor='none')
		ax.add_artist(patch2)
		patch3 = patches.PathPatch(path, fill=False, lw=1, linestyle="dotted")

		ax.add_patch(patch)
		ax.add_patch(patch3)
		patch.set_clip_path(patch2)

			
		xlim(0,1)
		ylim(0,1)


	def plot_membership(self, attribute="", adjective="", color="orange", ax=None):
		ax.set_xlabel(attribute)
		ax.set_ylabel("$\mu$")
		self.plot_polygon(verts=self.determine_polygon(attribute=attribute, adjective=adjective), clip=self.determine_membership(attribute=attribute, adjective=adjective), color=color, ax=ax)


	def get_adjectives(self, attribute):
		for name, var in self.fuzzySystem.variables.items():
			if name==attribute: 
				for name2, var2 in var.adjectives.items():
					yield name2

	def get_membership(self, attribute):
		""" Returns the list of the membership values for each adjective of attribute. """
		ret = {}
		for adj in self.get_adjectives(attribute):
			ret[adj] = self.determine_membership(attribute=attribute, adjective=adj)
		return ret


	def plot_all_membership(self, attribute, ax=None): 
		# print "Plotting membership of attribute", attribute
		for lab in self.get_adjectives(attribute):
			# print "- plotting membership of adjective", lab
			cl = self.determine_membership(attribute=attribute, adjective=lab)
			# print "-- membership:", cl
			self.plot_membership(attribute=attribute, adjective=lab, color=matplotlib.colors.colorConverter.to_rgb((cl*.2,cl,cl*.2)), ax=ax)

	def plot_actual_value(self, value, ax):
		ax.plot([value,value], [0,1], "--", lw=5)

	def plot_defuzzified_value_sugeno(self, value, maximum, ax):		
		ax.plot([value,value], [0,1], lw=5, color='#cccccc')
		ax.plot([value,value], [0,maximum], lw=5, color="black")


	def get_list_input_variables(self):
		ret = []
		for (k,v) in self.fuzzySystem.variables.items():
			if isinstance(v, fuzzy.InputVariable.InputVariable):
				ret.append(v.getName(self.fuzzySystem))
		return ret


	def plot_single_precalculated_membership(self, attribute=None, adjective=None, value=None, ax=None):
		self.plot_polygon(verts=self.determine_polygon(attribute=attribute, adjective=adjective), clip=value, color=matplotlib.colors.colorConverter.to_rgb((value*.2,value,value*.2)), ax=ax)

	def plot_precalculated_membership(self, attribute, ax=None, iteration=1):
		what_to_plot =  self.whole_memberships[attribute][iteration]
		for lab in what_to_plot.keys():
			cl = self.whole_memberships[attribute][iteration][lab]
			self.plot_single_precalculated_membership(attribute=attribute, adjective=lab, value=cl, ax=ax)
			
		self.plot_actual_value(self.whole_dynamics[attribute][iteration], ax)
		ax.set_xlabel(attribute)
		ax.set_ylabel("$\mu$")
		# ax.locator_params(nbins=3)


	def get_set_antecedents(self, ants, operator):
		if isinstance(operator, fuzzy.operator.Input.Input):
			ants.add(operator)
		elif isinstance(operator, fuzzy.operator.Compound.Compound):            
			for o in operator.inputs:
				self.get_set_antecedents(ants, o)
		else:
			print "ERROR processing antecedents"


	def get_set_consequents(self, cons, operator):
		if isinstance(operator, list):
			for con in operator:
				self.get_set_consequents(cons,con)
		else:
			cons.add(operator) 


	def get_list_antecedents(self, ants, operator):
		if isinstance(operator, fuzzy.operator.Input.Input):
			ants.append(operator)
		elif isinstance(operator, fuzzy.operator.Compound.Compound):            
			for o in operator.inputs:
				# ants.append()
				self.get_list_antecedents(ants, o)
		else:
			print "ERROR processing antecedents"


	def get_list_consequents(self, cons, operator):
		if isinstance(operator, list):
			for con in operator:
				self.get_list_consequents(cons,con)
		elif isinstance(operator, fuzzy.operator.Compound.Compound):
			for con in operator.cons:
				self.get_list_consequents(cons,con)
		else:
			cons.append(operator) 

	def get_adj_name_from_antecedent(self, adj):
		return str(adj.adjective.getName(self.fuzzySystem)[1])

	def get_adj_name_from_consequent(self, adj):
		return str(adj.getName(self.fuzzySystem)[1])


if __name__ == '__main__':
	
	fs = FuzzySystem(input_file="celde13.fcl")
	fs.create_groups_observed([["Survival"]])
	
	fs.state = {  
			"ATP": 1.0,
			"Apoptosis": 0.0,
			"Attach": 1.0,
			"Autophagy": 0.0,
			"BCN1": 0.0,
			"Bcl2": 1.0,
			"C1": 0.5,
			"CA2": 0.0,
			"CHOP": 0.0,
			"Caspase3": 0.0,
			"DAPK": 0.0,
			"DeltaPsi": 1.0,
			"ERKPI3K": 1.0,				
			"Glucose": 1.0,
			"Glycolysis": 1.0,		
			"HBP": 1.0,
			"JNK": 0.0,		
			"NGlycos": 1.0,
			"Necrosis": 0.0,			
			"ROS": 0.5,
			"Src": 1.0,
			"Survival": 1.0,		
			"UPR": 0.0,		
			"Time": 0.0
	}

	store_everything = False
	fs.set_state_updaters([[u'PKA', fun1, [[0,1]] ], [u"RasGTP", fun2, [ [0,1]] ]])
	fs.simulate( Sugeno=True, verbose=True, iterations=10, store_everything=store_everything )
	
	if store_everything:
		for k, v in fs.whole_dynamics.items():
			print k, v
	else:
		for k, v in fs.observed_elements.items():
			print k, v
