import time
import heapq as hq
import logging
import os,csv, shutil
import argparse
import math
from preprocessing import convertSignals2Traces
from smtencoding import SMTEncoding
from signaltraces import Sample, Trace, Signal
from formula import STLFormula
from z3 import *
from STLmonitoring.main import genBooleanSat
from main import genBooleanSat

class learnSTL:

	def __init__(self, signalfile, checking_dir=None):


		self.signalfile = signalfile
		self.signal_sample = Sample()
		self.signal_sample.readSample(self.signalfile)

		#self.predicates = 
		self.size_bound = 5
		self.fr_bound = 4
		self.search_order = [(i,j) for i in range(1, self.fr_bound+1,5) for j in range(1, self.size_bound+1)] #can try out other search orders
		self.predicates = self.signal_sample.predicates
		#print(self.search_order)
		self.checking_dir = checking_dir


		if self.checking_dir != None:

			if os.path.exists(self.checking_dir):
   				shutil.rmtree(self.checking_dir)
   				os.makedirs(self.checking_dir)

			for i,signal in enumerate(self.signal_sample.positive):
				
				signal_csv = []

				filename = self.checking_dir+'/positive'+str(i)+'.csv'
				with open(filename, 'w') as file:

					header = []
					writer = csv.writer(file)
					for v in self.signal_sample.vars:
						header.extend([v,v+'_t'])
					writer.writerow(header)

					for t in signal.sequence:
						info = []
						for j in range(len(self.signal_sample.vars)):
							info.extend([t.vector[j], t.time]) 
						writer.writerow(info)
					

			for i,signal in enumerate(self.signal_sample.negative):
				
				signal_csv = []
				filename = self.checking_dir+'/negative'+str(i)+'.csv'
				with open(filename, 'w') as file:

					writer = csv.writer(file)
					header = []
					for v in self.signal_sample.vars:
						header.extend([v,v+'_t'])
					writer.writerow(header)

					for t in signal.sequence:
						info = []
						for j in range(len(self.signal_sample.vars)):
							info.extend([t.vector[j], t.time]) 
						writer.writerow(info)
					

	def interesting_pred(self):
	
		pass
		#current assumption predicates are given

	#return #the predicates



	def truncate_sample(self, fr_score):
		'''
		Truncates the signals based on the future reach score
		'''

		#Possible optimization: Always no need to compute from scratch
		new_sample = Sample(positive=[], negative=[])
		new_sample.vars = self.signal_sample.vars
		new_sample.operators = self.signal_sample.operators
		new_sample.predicates = self.signal_sample.predicates

		for pos in self.signal_sample.positive:
			new_signal = Signal(sequence=[])
			for sp in pos.sequence:
				#print(sp.time)
				if sp.time <= fr_score:
					new_signal.addPoint(sp)
				else:
					break
			new_sample.positive.append(new_signal)


		for neg in self.signal_sample.negative:
			new_signal = Signal(sequence=[])
			for sp in neg.sequence:
				if sp.time <= fr_score:
					new_signal.addPoint(sp)
				else:
					break
			new_sample.negative.append(new_signal)

		return new_sample


	def calcUTP(self, itp):
		'''
		Calculates the uniform time points from interesting time points
		'''
		# Assuming that the time points have upto 3 decimals
		if len(itp) <= 1:
			return itp

		new_diff = int(1000*(round(itp[1]-itp[0],3)))
		for i in range(len(itp)-1):
		
			diff = int(1000*(round(itp[i+1]-itp[i],3)))
			new_diff = math.gcd(diff, new_diff)

		#new_diff = math.gcd(*diff_list)/1000
		gcd = new_diff/1000

		print('GCD value: ', gcd)
		start_time = itp[0]
		end_time = itp[-1]
		#print((end_time-start_time)/new_diff)
		
		utp = [round(start_time+i*gcd,3) for i in range(int((end_time-start_time)/gcd))]

		utp.append(end_time)
		return utp

	def calcNewTP(self, itp):

		add_itp = [round(itp[j]-itp[i],3) for i in range(len(itp)) for j in range(i,len(itp))]
		utp = sorted(list(set(itp + add_itp)))
		
		return utp



	def search(self):
		found_formula_size= 5
		'''
		Searches for appropriate MTL formulas for the given predicates
		'''
		for fr in [1]:
		#for fr in range(1,self.fr_bound+1):

			print('***************Fixing fr to be %d***************'%fr)
			curr_sample = self.truncate_sample(fr)
			binary_sample, alphabet, prop2pred, itp = convertSignals2Traces(curr_sample) # possible optimization to add only new points
			#print(type(binary_sample.positive[0]))
			binary_sample.writeToFile('dumm_%d.trace'%fr)
			print(itp)

			utp = self.calcUTP(itp)
			
			#utp = self.calcNewTP(itp)
			
			#print(itp)
			print(utp)
			#print(utp1)


			print('* Number of interesting time points: %d'%len(itp))
			#print('* Number of new interesting time points: %d'%len(utp))
			print('* Number of uniformized time points: %d'%len(utp))

			for formula_size in [2]:
			#for formula_size in range(1,found_formula_size+1): 
			#for formula_size in range(1,self.size_bound+1): 
				print('---------------Searching for formula size %d---------------'%formula_size)
				encoding = SMTEncoding(binary_sample, formula_size, alphabet, itp, utp, prop2pred)
				encoding.encodeFormula()
				
				solverRes = encoding.solver.check()
				#t_solve=time.time()-t_solve

				checking= encoding.solver.unsat_core()
				#print(checking)

				#Print this to see constraint creation time and constraint solving time separately
				#print(depth, regexDepth)
				#print((i,j), "Creating time:", t_create, "Solving time:", t_solve)
				print('The solver found', solverRes)

				if solverRes == sat:
					solverModel = encoding.solver.model()
					#print(solverModel.eval(self.x[2,'G']))
					'''
					for t in solverModel.decls():
  						if is_true(solverModel[t]):		
  							print(type(t),t)
  					'''

					formula = encoding.reconstructWholeFormula(solverModel)
					self.check_consistency(formula)
					print(formula.prettyPrint())
					#found_formula_size= formula.size
					print(found_formula_size)
					break



	def check_consistency(self, formula):

		formula_str = formula.prettyPrint()

		#convert F, G, ! to <>, [], -
		formula_str = formula_str.replace('[','{')
		formula_str = formula_str.replace(']','}')
		formula_str = formula_str.replace('F', '<>')
		formula_str = formula_str.replace('G', '[]')
		formula_str = formula_str.replace('!', '-')
		
		formulafile = self.checking_dir + '/formula.stl'
		with open(formulafile, 'w') as file:
			file.write(formula_str)

		for i,signal in enumerate(self.signal_sample.positive):
				
			filename = self.checking_dir+'/positive'+str(i)+'.csv'
			print(filename)
			print(genBooleanSat(formulafile=formulafile, signalfile=filename, semantics='boolean', algorithm='efficient'))

		for i,signal in enumerate(self.signal_sample.negative):
			
			filename = self.checking_dir+'/negative'+str(i)+'.csv'
			print(filename)
			print(genBooleanSat(formulafile=formulafile, signalfile=filename, semantics='boolean', algorithm='efficient'))
	





def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--input_file', '-i', dest='input_file', default = './simple1.signal')
	parser.add_argument('--timeout', '-t', dest='timeout', default=900, type=int)
	parser.add_argument('--outputcsv', '-o', dest='csvname', default= './result.csv')
	parser.add_argument('--verbose', '-v', dest='verbose', default=3, action='count')
	args,unknown = parser.parse_known_args()
	
	input_file = args.input_file
	timeout = float(args.timeout)

	learner = learnSTL(signalfile=input_file,checking_dir='check')
	learner.search()


main()

