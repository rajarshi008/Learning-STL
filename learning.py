from signal import Sample, samplePoint, Signal, WordSample, Trace, binarySignal


# read sample, predicates
sample = Sample()
sample.readSample('cart-pole.signal')

print(sample.predicates)

start_time = sample.positive[0].sequence[0].time # all signals start at same time
#end_time = sample.positive[0].sequence[-1].time # all signals end at same time

binary_signals = {}
interesting_time_points = {start_time}

for signal in sample.positive+sample.negative:

	end_time = signal.sequence[-1].time
	for i in range(len(sample.vars)):
		var = sample.vars[i]
		
		for c in sample.predicates[var]:
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

				t0 = ((t2-t1)*c + var2*t1 - var1*t2)/(var2-var1)

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
wordsample = WordSample(positive=[], negative=[])

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


	for t in interesting_time_points:
		
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

	trace_vector = []
	for sp in timed_word.sequence:
		trace_vector.append(tuple(sp.vector))

	if label_decider <= num_pos:

		positive_set.add(Trace(vector=trace_vector))
	else:
		negative_set.add(Trace(vector=trace_vector))


wordsample.positive = list(positive_set)
wordsample.negative = list(negative_set)

wordsample.writeToFile("please.trace")
			




