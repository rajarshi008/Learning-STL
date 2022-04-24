def convertTextToSignal(text):

	sequence = []
	split1 = text.split(';')
	for value in range(split1):
		time, vector = value.split(':')
		vector = [float(i) for i in vector.split(',')]
		sp = samplePoint(float(time), vector)
		sequence.append(sp)

	return Signal(sequence)



default_operators = ['&', '|', '!', 'F', 'G', 'U']


class samplePoint:
	
	def __init__(self, time, vector):

		self.time = time
		self.vector = vector
		self.size = len(vector)

	def __str__(self):

		text = str(self.time) + ':' 
		text += ','.join([str(i) for i in self.vector])
		return text

class Signal:
	
	def __init__(self, sequence):

		if sequence==[] or isinstance(sequence[0], samplePoint):
			self.sequence = sequence
		else:
			raise Exception("Invalid signals")

	def addPoint(self, samplePoint):

		self.sequence.append(samplePoint)

	def calculateInfo(self):

		self.domain = [i.time for i in self.sequence]

	def __str__(self):

		text = ';'.join([str(value) for value in self.sequence])
		return text


class Sample:

	def __init__(self, positive=[], negative=[], vars=[], operators=[]):

		self.positive = positive
		self.negative = negative
		self.vars = []
		if operators==[]:
			self.operators = default_operators
		else:
			self.operators = operators

		self.predicates = {}

	def readSample(signalfile):
		
		with open(signalfile, 'r') as file:
			mode = 0
			count=0
			while True:
				count
				line=file.readline()
				if line=='':
					break

				if line == '---\n':
					mode+=1
					continue

				if mode==0:	
		
					signal = convertTextToSignal(line)	 	
					self.numVars = signal.sequence[0].size
					self.positive.append(signal)


				if mode==1:
					
					signal = convertTextToSignal(line)
					self.negative.append(signal)
					
				if mode==2:
				
					self.operators = list(line.strip().split(','))
				
				if mode==3:

					self.vars = list(line.strip().split(','))

				if mode==4:

					if self.vars == []:
						self.vars = ['x'+str(i) for i in range(self.numVars)]

					line = line.split(';')
					if len(line) != len(self.vars):
						raise Exception("Not enough predicates")

					for i in range(len(line)):
						self.predicates[self.vars[0]] = [float(j) for j in line[i].split(',')]
		
		
	def writeSample(self, signalfile):

		with open(signalfile, 'w') as file:
			
			for signal in self.positive:
				file.write(str(signal)+'\n')

			file.write('---\n')
			for signal in self.negative:
				file.write(str(signal)+'\n')

			file.write('---\n')

			file.write(','.join(self.operators)+'\n')

			file.write('---\n')

			file.write(','.join(self.vars)+'\n')

			file.write('---\n')

			pred_list = []
			for var in self.vars:
				pred_list.append(','.join([str(i) for i in self.predicates[var]]))
			
			file.write(';'.join(pred_list))










