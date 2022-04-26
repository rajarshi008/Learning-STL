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
	'''
	signals are finite piece-wise linear continuous functions
	'''
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


class binarySignal:
	'''
	binarySignals are finite piece-wise linear (possibly discontinuous) functions
	'''
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





class WordSample:
	'''
	contains the sample of postive and negative examples
	'''
	def __init__(self, positive=[], negative=[], alphabet=[], is_words=False, operators=['G', 'F', '!', 'U', '&','|', 'X']):

		self.positive = positive
		self.negative = negative
		self.alphabet = alphabet
		self.is_words = is_words
		self.num_positives = len(self.positive)
		self.num_negatives = len(self.negative)
		self.operators=operators

	
	def extract_alphabet(self, is_word):
		'''
		extracts alphabet from the words/traces provided in the data
		'''
		alphabet = set()
		
		if self.is_words:
			for w in self.positive+self.negative:
				alphabet = alphabet.union(set(w.vector))
			self.alphabet = list(alphabet)
		else:
			self.alphabet = [chr(ord('p')+i) for i in range(len(self.positive[0].vector[0]))] 

	def word2trace(self, word):
		one_hot_alphabet={}
		for i in range(len(self.alphabet)):
			one_hot_letter = [0]*len(self.alphabet)
			letter = self.alphabet[i]
			one_hot_letter[i] = 1
			one_hot_alphabet[letter] = tuple(one_hot_letter)
		trace_list=[]
		for letter in word:
			trace_list.append(one_hot_alphabet[letter])

		return trace_list



	def readFromFile(self, filename):
		'''
		reads .trace/.word files to extract sample from it
		'''
		self.is_words = ('.words' in filename)
		with open(filename, 'r') as file:
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
					# can read from both word file type and trace file type
					if self.is_words:
						word_vector, lasso_start = lineToWord(line)
						word = Trace(vector=word_vector, lasso_start=lasso_start, is_word=True)	 	
						self.positive.append(word)
					else:
						trace_vector, lasso_start = lineToTrace(line)
						trace = Trace(vector=trace_vector, lasso_start=lasso_start, is_word=False)	 	
						self.positive.append(trace)

				if mode==1:
					
					if self.is_words:
						word_vector, lasso_start = lineToWord(line)
						word = Trace(vector=word_vector, lasso_start=lasso_start, is_word=True)	 	
						self.negative.append(word)
					else:
						trace_vector, lasso_start = lineToTrace(line)
						trace = Trace(vector=trace_vector, lasso_start=lasso_start, is_word=False)	 	
						self.negative.append(trace)

				if mode==2:
					self.operators = list(line.strip().split(','))
				if mode==3:
					self.alphabet = list(line.split(','))


		if mode != 3:		
				self.extract_alphabet(self.is_words)
		
		self.letter2pos={}
		for i in range(len(self.alphabet)):
			self.letter2pos[self.alphabet[i]]=i
		
		if self.is_words:
			for word in self.positive+ self.negative:
				word.vector= self.word2trace(word.vector)
				word.vector_str= str(word.vector)
				word.is_word = False

		self.writeToFile('small-example')

	def writeToFile(self, filename):

		with open(filename, 'w') as file:
			for trace in self.positive:

				file.write(str(trace)+'\n')
			file.write('---\n')

			for trace in self.negative:
				file.write(str(trace)+'\n')


			if self.operators!=[]:
				file.write('---\n')
				file.write(','.join(self.operators)+'\n')

			if self.alphabet != []:
				file.write('---\n')
				file.write(','.join(self.alphabet))


