import time
import heapq as hq
import logging
import csv
from preprocessing import convertSignals2Trace
from smtencoding import SMTEncoding
from signaltraces import Sample, Trace




class learnSTL:

	def __init__(self, signalfile):


		self.signalfile = signalfile
		self.signal_sample = Sample()
		self.signal_sample.readSample(self.signalfile)
		#self.predicates = 
		self.size_bound = 20
		self.fr_bound = 10
		self.search_order = [(i,j) for i in range(1, self.fr_bound+1) for j in range(1, self.size_bound+1)] #can try out other search orders
		self.predicates = self.signal_sample.predicates

	def interesting_pred(self):
	'''
	Suggested interesting predicates to construct STL formula
	'''
	pass
	#current assumption predicates are given

	#return #the predicates



	def truncate_sample(self, fr_score);
	'''
	Truncates the signals based on the future reach score
	'''

	#Possible optimization: Always no need to compute from scratch
		new_sample = Sample()

		for pos in self.signal_sample.positive:
			new_signal = Signal()
			for sp in pos.sequence:
				if sp.time <= fr_score:
					new_signal.addPoint(sp)
				else:
					break
			new_sample.positive.append(new_signal)

		for neg in self.signal_sample.negative:
			new_signal = Signal()
			for sp in neg.sequence:
				if sp.time <= fr_score:
					new_signal.addPoint(sp)
				else:
					break
			new_sample.negative.append(new_signal)

		return new_sample


	def calcUTP(self, itp):

		# Assuming that the time points have upto 3 decimals
		new_diff = int(1000*(round(itp[1]-itp[0],3)))
		for i in range(len(itp)-1):
		
			diff = int(1000*(round(itp[i+1]-itp[i],3)))
			new_diff = math.gcd(diff, new_diff)

		#new_diff = math.gcd(*diff_list)/1000
		new_diff = new_diff/1000

		start_time = itp[0]
		end_time = itp[-1]
		utp = [start_time+i*new_diff for i in range((end_time-start_time)/new_diff)]

		return utp

	def search(self, search_order):
		'''
		searches for appropriate MTL formulas for the given predicates
		'''

		for (fr, formula_size) in search_order:

			curr_sample = self.truncate_sample(fr)
			binary_sample, alphabet, itp, prop2pred = convertSignals2Trace(curr_sample) # possible optimization to add only new points
			utp = self.calcUTP(itp)
			encoding = SMTEncoding(curr_sample, formula_size, alphabet, itp, utp)
			






def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--input_file', '-i', dest='input_file', default = './example.signal')
	parser.add_argument('--timeout', '-t', dest='timeout', default=900, type=int)
	parser.add_argument('--outputcsv', '-o', dest='csvname', default= './result.csv')
	parser.add_argument('--verbose', '-v', dest='verbose', default=3, action='count')
	parser.add_argument('--method', '-m', dest='method', default = 'SC')
	parser.add_argument('--words', '-w', dest= 'words', default = False, action='store_true')
	parser.add_argument('-thres', '-l', dest='thres', default=0)
	args,unknown = parser.parse_known_args()

	input_file = args.input_file
	is_word = True if ('.words' in input_file) or args.words  else False
	timeout = float(args.timeout)
	verbosity = int(args.verbose)-1
	method = args.method
	csvname = args.csvname
	thres = float(args.thres)
	last = False


	learner = LTLlearner(is_word=is_word, timeout=timeout, verbosity=verbosity,
												method=method, thres=thres,last=last)
	learner.learn(tracefile=input_file, outputfile=csvname)





