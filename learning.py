import Sample, samplePoint, Signal


# read sample, predicates
sample = Sample()
sample.readSample()


start_time = sample.positive[0].sequence[0].time # all signals start at same time
end_time = sample.positive[0].sequence[-1].time # all signals end at same time

binary_signals = {}
interesting_time_points = {start_time,end_time}

for signal in sample.positive:

	for i in range(len(sample.vars)):
		var = sample.vars[i]
		
		for c in sample.predicates[var]:
			#Optimization: there is relation between the binary signals for same var

			start_value = 1 if signal.sequence[0].vector[i] - c > 0 else 0
			curr_binary_signal = binarySignal([samplePoint(time=starting_time, vector=[starting_value])])


			for j in range(len(signal)-1):
				
				sp1 = signal.sequence[j]
				sp2 = signal.sequence[j+1]
				
				t1 = sp1.time
				var1 = sp1.vector[i]
				
				t2 = sp2.time
				var2 = sp2.vector[i]

				t0 = ((t2-t1)*c + var2*t1 - var1*t2)/(var2-var1)

				if t0 < t1 or t0 > t2 or t0 == start_time or t0 == end_time:
					continue
				else:
					interesting_time_points.add(t0)
					curr_value = 1 - curr_binary_signal.sequence[-1].vector[0]
					curr_binary_signal.addPoint(samplePoint(time=t0, vector=[curr_value])) 

			end_value = 1 if signal.sequence[-1].vector[i] - c > 0 else 0
			curr_binary_signal.addPoint(samplePoint(time=end_time, vector=[end_value]))


			binary_signals[(signal,var,c)] = curr_binary_signal




for signal in sample.positive:

	binary
	for i in range(len(sample.vars)):
		var = sample.vars[i]
		for c in sample.predicates[var]:
			

			binary_signals[(signal,var,c)]




