from signaltraces import Sample, samplePoint, Signal, WordSample, Trace, binarySignal
#from Scarlet.inferLTL import inferLTL
#from Scarlet.formulaTree import Formula
from formula import LTLFormula, STLFormula
import math



def convertSignals2Traces(sample, wordsamplefile='example.trace', operators=['F', 'X', '&', '|', '!']):
	'''
	takes a sample of signals and produces a equivalent sample of traces in wordsamplefile
	'''

	start_time = sample.positive[0].sequence[0].time # all signals start at same time
	#end_time = sample.positive[0].sequence[-1].time # all signals end at same time
	#print(sample.vars)

	print(sample.positive[0])

	binary_signals = {}
	interesting_time_points = {start_time}
	for i in range(len(sample.vars)):
		var = sample.vars[i]
		for c in sample.predicates[var]:
			
			for signal in sample.positive+sample.negative:

				end_time = signal.sequence[-1].time
				#print(signal)
				#Optimization: there is relation between the binary signals for same var
				
				start_value = 1 if signal.sequence[0].vector[i] - c > 0 else 0
				curr_binary_signal = binarySignal([samplePoint(time=start_time, vector=[start_value])])


				for j in range(len(signal.sequence)-1):
					
					sp1 = signal.sequence[j]
					sp2 = signal.sequence[j+1]
					
					t1 = sp1.time
					var1 = sp1.vector[i]
					
					t2 = sp2.time
					var2 = sp2.vector[i]

					if var1 == var2:
						continue

					t0 = round(((t2-t1)*c + var2*t1 - var1*t2)/(var2-var1),1)

					if t0 < t1 or t0 > t2 or t0 == start_time or t0 == end_time:
						continue
					else:
						interesting_time_points.add(t0)
						curr_value = 1 - curr_binary_signal.sequence[-1].vector[0]
						curr_binary_signal.addPoint(samplePoint(time=t0, vector=[curr_value])) 

				interesting_time_points.add(end_time)
				end_value = 1 if signal.sequence[-1].vector[i] - c > 0 else 0
				curr_binary_signal.addPoint(samplePoint(time=end_time, vector=[end_value]))


				binary_signals[(signal,var,c)] = curr_binary_signal


	interesting_time_points = sorted(list(interesting_time_points))

	abs_start_time = interesting_time_points[0] 
	abs_end_time = interesting_time_points[-1]
	interval_map = {}
	#print(len(interesting_time_points))
	#for i in range(len(interesting_time_points)-1):
	#interval_map[i] = (interesting_time_points[i],interesting_time_points[i+1])

	
	wordsample = WordSample(positive=[], negative=[])

	i=0
	prop2pred = {}
	for var in sample.vars:
		for c in sample.predicates[var]:
			#print(var,c)
			prop2pred['p'+str(i)] = '('+str(var)+'>'+str(c)+')'
			i+=1
	wordsample.alphabet = list(prop2pred.keys())

	label_decider = 0
	num_pos = len(sample.positive)
	positive_set = set()
	negative_set = set()

	for signal in sample.positive+sample.negative:

		label_decider += 1

		head = {}
		end_time = signal.sequence[-1].time

		start_value = []
		for var in sample.vars:
			for c in sample.predicates[var]:
				head[(var,c)] = 0
				start_value.append(binary_signals[(signal,var,c)].sequence[0].vector[0])


		timed_word = binarySignal([samplePoint(time=start_time, vector=start_value)])


		for t in interesting_time_points[1:]:
			
			if t > end_time:
				break

			curr_value = []
			for var in sample.vars:
				for c in sample.predicates[var]:

					next_head_time = binary_signals[(signal,var,c)].sequence[head[(var,c)]+1].time

					if t == next_head_time:

						head[var,c] += 1
						curr_value.append(binary_signals[(signal,var,c)].sequence[head[(var,c)]].vector[0])

					else:

						curr_value.append(binary_signals[(signal,var,c)].sequence[head[(var,c)]].vector[0])

			timed_word.addPoint(samplePoint(time=t, vector=curr_value))
		#print(timed_word, len(timed_word.sequence))
		
		trace_vector = []
		for sp in timed_word.sequence:
			trace_vector.append(tuple(sp.vector))

		if label_decider <= num_pos:

			positive_set.add(Trace(vector=trace_vector))
		else:
			negative_set.add(Trace(vector=trace_vector))


	wordsample.positive = list(positive_set)
	wordsample.negative = list(negative_set)
	#wordsample.operators = operators


	#print(sample.predicates)

	#wordsample.writeToFile(wordsamplefile)
	
	return wordsample, wordsample.alphabet, prop2pred, interesting_time_points


def uniformIntervals(wordsample, uniform_sample_file, interval_map, abs_start_time, abs_end_time):

	new_diff = int(1000*(round(interval_map[0][1]-interval_map[0][0],3)))
	for i in list(interval_map.keys())[1:]:
		
		diff = int(1000*(round(interval_map[i][1]-interval_map[i][0],3)))
		new_diff = math.gcd(diff, new_diff)

	#new_diff = math.gcd(*diff_list)/1000
	new_diff = new_diff/1000

	i0 = abs_start_time
	i1 = abs_start_time + new_diff
	new_interval_map={}
	c = 0	
	while i1 < abs_end_time:
		new_interval_map[c] = (i0,i1)
		i0 = i1  
		i1 = i1+new_diff
		c+=1

	new_word_sample = WordSample(positive=[], negative=[])
	for word in wordsample.positive:
		new_word = Trace(vector = [])
		for i in range(len(word.vector)-1):
			new_word.vector+=[word.vector[i]]*(int(round((interval_map[i][1]-interval_map[i][0]),3)/new_diff))
		new_word.vector.append(word.vector[len(word.vector)-1])
		
		new_word_sample.positive.append(new_word)


	for word in wordsample.negative:
		new_word = Trace(vector = [])
		for i in range(len(word.vector)-1):
			new_word.vector+=[word.vector[i]]*(int(round((interval_map[i][1]-interval_map[i][0]),3)/new_diff))
		new_word.vector.append(word.vector[len(word.vector)-1])
		new_word_sample.negative.append(new_word)

	new_word_sample.writeToFile(uniform_sample_file)

	return new_word_sample, new_interval_map 



def refineltl(ltlformula):
	'''
	Only suitable for formulas from Scarlet
	'''
	curr_label = ltlformula.label
	new_formula = Formula()

	if curr_label == 'X':
		
		#print('this')
		f = refineltl(ltlformula.left)

		if f.label == 'F':
			new_formula = ltlformula

		if f.label == 'X':

			#print('that')
			new_formula.label = ('X',2)
			new_formula.left = f.left


		elif isinstance(f.label, tuple):

			new_formula.label = ('X',f.label[1]+1)
			new_formula.left = f.left

		elif f.label == '&' or f.label == '|':
			
			new_formula.label = f.label
			inter_formula1 = Formula()
			inter_formula1.label = 'X'
			inter_formula1.left = f.left

			inter_formula2 = Formula()
			inter_formula2.label = 'X'
			inter_formula2.left = f.right

			new_formula.left = refineltl(inter_formula1)
			new_formula.right = refineltl(inter_formula2)

		else:

			new_formula = ltlformula


	elif isinstance(curr_label, tuple):

		f = refineltl(ltlformula.left)

		if f.label == 'F':
			new_formula = ltlformula

		if f.label == 'X':

			new_formula.label = ('X',curr_label[1]+1)
			new_formula.left = f.left

		elif isinstance(f.label, tuple):

			new_formula.label = ('X',f.label[1]+curr_label[1])
			new_formula.left = f.left

		elif f.label == '&' or f.label == '|':
			
			new_formula.label = f.label
			inter_formula1 = Formula()
			inter_formula1.label = curr_label
			inter_formula1.left = f.left

			inter_formula2 = Formula()
			inter_formula2.label = curr_label
			inter_formula2.left = f.right

			new_formula.left = refineltl(inter_formula1)
			new_formula.right = refineltl(inter_formula2)

		else:

			new_formula = ltlformula


	elif curr_label == 'F':

		f = refineltl(ltlformula.left)

		if f.label == 'F':
			new_formula = f

		elif f.label == 'G':

			new_formula.label = 'F'
			new_formula.left = f

		elif f.label == 'X':

			inter_formula = Formula()
			inter_formula.label = 'F'
			inter_formula.left = f.left

			new_formula.label = 'X'
			new_formula.left = refineltl(inter_formula)

		elif isinstance(f.label, tuple):

			inter_formula = Formula()
			inter_formula.label = 'F'
			inter_formula.left = f.left

			new_formula.label = f.label
			new_formula.left = refineltl(inter_formula)

		elif f.label == '|':
			
			inter_formula1 = Formula()
			inter_formula1.label = 'F'
			inter_formula1.left = f.left

			inter_formula2 = Formula()
			inter_formula2.label = 'F'
			inter_formula2.left = f.right

			new_formula = f.label
			new_formula.left = refineltl(inter_formula1)
			new_formula.right = refineltl(inter_formula2)

		else:
			new_formula = ltlformula

	elif curr_label == 'G':

		f = refineltl(ltlformula.left)

		if f.label == 'F':
			new_formula = f

		elif f.label == 'G':
			new_formula = f.left


		elif f.label == 'X':

			inter_formula = Formula()
			inter_formula.label = 'G'
			inter_formula.left = f.left

			new_formula.label = 'X'
			new_formula.left = refineltl(inter_formula)

		elif isinstance(f.label, tuple):

			inter_formula = Formula()
			inter_formula.label = 'G'
			inter_formula.left = f.left

			new_formula.label = f.label
			new_formula.left = refineltl(inter_formula)

		elif f.label == '&' or f.label == '|':
			
			raise Exception("Cannot return equivalent STL formula")
		else:
			new_formula = ltlformula


	elif curr_label == '&' or curr_label == '|':
		
		f1 = refineltl(ltlformula.left)
		f2 = refineltl(ltlformula.right)
		new_formula.label = curr_label
		new_formula.left = f1
		new_formula.right = f2
	else:
		new_formula = ltlformula

	return new_formula

		

# ltl2stl
# Scarlet remove F from len 1


def ltl2stl(ltlformula, interval_map, alphabet, prop2pred, start_time, end_time, temporal):
	'''
	write an inductive definition
	'''
	#refined = refineltl(ltlformula)
	#print(start_time, end_time)
	stl_formula = STLFormula()
	#start_time = interval_map[0][0]
	#end_time = interval_map[-1][1]

	if ltlformula.label in alphabet:

		if temporal:
			stl_formula = STLFormula([('G',interval_map[0]),prop2pred[ltlformula.label], None])
		else:
			stl_formula = STLFormula([prop2pred[ltlformula.label], None, None])

	elif ltlformula.label == '!':

		stl_formula.label = ltlformula.label
		stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred, start_time, end_time, temporal)
		stl_formula.right = None

	#if ltlformula.label in alphabet or ltlformula.
	elif ltlformula.label == '&' or ltlformula.label == '|':

		stl_formula.label = ltlformula.label
		stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred, start_time, end_time, temporal)
		stl_formula.right = ltl2stl(ltlformula.right, interval_map, alphabet, prop2pred, start_time, end_time, temporal)


	elif ltlformula.label == 'X':
		
		stl_formula.right = None

		if ltlformula.left.label == 'F':
			stl_formula.label = ('F',(interval_map[1][1],end_time))
			stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred, start_time, end_time, temporal=False)


		elif ltlformula.left.label in alphabet or ltlformula.left.label == '!':
			stl_formula.label = ('G',interval_map[1])
			stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred, start_time, end_time, temporal=False)

	elif isinstance(ltlformula.label, tuple):

		stl_formula.right = None

		if ltlformula.left.label == 'F':

			stl_formula.label = ('F',(interval_map[ltlformula.label[1]][1], end_time))
			stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred, start_time, end_time, temporal=False)

		elif ltlformula.left.label in alphabet or ltlformula.left.label == '!':
			
			stl_formula.label = ('G',interval_map[ltlformula.label[1]])
			stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred, start_time, end_time, temporal=False)

	elif ltlformula.label == 'F':

		stl_formula.right = None
		stl_formula.label = ('F', (start_time, end_time))
		stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred,  start_time, end_time, temporal=False)

	
	elif ltlformula.label == 'G':

		stl_formula.right = None
		stl_formula.label = ('G', (start_time, end_time))
		stl_formula.left = ltl2stl(ltlformula.left, interval_map, alphabet, prop2pred,  start_time, end_time, temporal=False)

	return stl_formula




'''
def learnSTL(signalfile):
	
	sample = Sample()
	sample.readSample(signalfile)

	wordsamplefile = signalfile.split('.')[0]+'.trace'
	uniformsamplefile= signalfile.split('.')[0] + 'uniform.trace'
	wordsample, alphabet, interval_map, prop2pred, start_time, end_time = convertSignals2Traces(sample, wordsamplefile, ['F', 'X', '&', '|', '!'])
	new_sample, new_interval_map= uniformIntervals(wordsample, uniformsamplefile, interval_map, start_time, end_time)
	print('Length of traces are '+ str(len(sample.positive[0].sequence)))
	print('Number of intervals without uniformization is '+ str(len(interval_map)))
	print('Number of intervals with uniformization is '+ str(len(new_interval_map)))
	

	ltllearning = ['Scarlet']

	if 'Scarlet' in ltllearning:

		ltlformula = inferLTL(uniformsamplefile,'output.csv')

	#print(ltlformula)
	f = refineltl(ltlformula)
	print(f.prettyPrint())
	#final_formula = ltl2stl(f, new_interval_map, alphabet, prop2pred, start_time, end_time, True)
	#print(final_formula.prettyPrint())

learnSTL('cart-pole.signal')
'''