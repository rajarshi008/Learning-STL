import csv


#read time
time_file = open('navalTimes', 'r')
data_file = open('navalData', 'r')
label_file = open('navalLabels', 'r')

time_reader = csv.reader(time_file)
data_reader = csv.reader(data_file)
label_reader = csv.reader(label_file)

timepoints = list(time_reader)[0]
labels = list(label_reader)[0]

positives = []
negatives = []

#manipulate data
data_list = list(data_reader)
#print(labels)

for i in range(len(data_list)):
	#print(i)
	row = data_list[i]
	x_values = list(row)[::2]
	y_values = list(row)[1::2]
	signal = list(zip(x_values, y_values))
	if i==0:
		print(signal)
	if labels[i]=='1':
		positives.append(signal)
		#print('holo')
	else:
		negatives.append(signal)
		#print('holo na')

trace_file = open('maritime.signal', 'w')
for signal in positives:
	signal_line = ''
	for t in range(len(timepoints)):
		signal_line += str(timepoints[t])+':'+str(signal[t][0])+','+str(signal[t][1])+';'
	
	signal_line = signal_line[:-1]+'\n'
	trace_file.write(signal_line)
 		
trace_file.write('---\n')
for signal in negatives:
	signal_line = ''
	for t in range(len(timepoints)):
		signal_line += str(timepoints[t])+':'+str(signal[t][0])+','+str(signal[t][1])+';'
	signal_line = signal_line[:-1]+'\n'
	trace_file.write(signal_line)
 	
trace_file.close()
time_file.close()
data_file.close()
label_file.close()