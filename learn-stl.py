import time
import heapq as hq
import logging
import csv
import argparse
import math
from preprocessing import convertSignals2Traces
from smtencoding import SMTEncoding
from signaltraces import Sample, Trace, Signal
from formula import STLFormula
from z3 import *


class learnSTL:

	def __init__(self, signalfile):


		self.signalfile = signalfile
		self.signal_sample = Sample()
		self.signal_sample.readSample(self.signalfile)
		#self.predicates = 
		self.size_bound = 5
		self.fr_bound = 2
		self.search_order = [(i,j) for i in range(1, self.fr_bound+1) for j in range(1, self.size_bound+1)] #can try out other search orders
		self.predicates = self.signal_sample.predicates
		print(self.search_order)


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
		new_diff = int(1000*(round(itp[1]-itp[0],3)))
		for i in range(len(itp)-1):
		
			diff = int(1000*(round(itp[i+1]-itp[i],3)))
			new_diff = math.gcd(diff, new_diff)

		#new_diff = math.gcd(*diff_list)/1000
		new_diff = new_diff/1000

		start_time = itp[0]
		end_time = itp[-1]
		print((end_time-start_time)/new_diff)
		
		utp = [start_time+i*new_diff for i in range(int((end_time-start_time)/new_diff))]

		return utp

	def search(self):
		'''
		Searches for appropriate MTL formulas for the given predicates
		'''
		
		for (fr, formula_size) in self.search_order:

			print('---------------Searching for order (%d,%d)---------------'%(fr,formula_size))
			curr_sample = self.truncate_sample(fr)
			binary_sample, alphabet, prop2pred, itp = convertSignals2Traces(curr_sample) # possible optimization to add only new points
			#print(type(binary_sample.positive[0]))

			utp = self.calcUTP(itp)

			encoding = SMTEncoding(binary_sample, formula_size, alphabet, itp, utp)
			encoding.encodeFormula()
			
			solverRes = encoding.solver.check()
			#t_solve=time.time()-t_solve

			#Print this to see constraint creation time and constraint solving time separately
			#print(depth, regexDepth)
			#print((i,j), "Creating time:", t_create, "Solving time:", t_solve)
			
			if solverRes == sat:
				solverModel = encoding.solver.model()
				formula = encoding.reconstructWholeFormula(solverModel)
				results.append(formula)
				print(formula.pettyPrint())
				break



def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--input_file', '-i', dest='input_file', default = './cart-pole.signal')
	parser.add_argument('--timeout', '-t', dest='timeout', default=900, type=int)
	parser.add_argument('--outputcsv', '-o', dest='csvname', default= './result.csv')
	parser.add_argument('--verbose', '-v', dest='verbose', default=3, action='count')
	args,unknown = parser.parse_known_args()

	input_file = args.input_file
	timeout = float(args.timeout)


	learner = learnSTL(input_file)
	learner.search()



main()

