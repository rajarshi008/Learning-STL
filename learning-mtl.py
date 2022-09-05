from preprocessing import convertSignals2Trace




class SMTEncoding:

	def __init__(self, size, fr, testTraces, interestingPoints): 
		
		defaultOperators = ['G', 'F', '!', '&','|', '->']
		unary = ['G', 'F', '!']
		binary = ['&', '|', '->']
		#except for the operators, the nodes of the "syntax table" are additionally the propositional variables 
		
		if testTraces.operators == None:
			self.listOfOperators = defaultOperators
		else:
			self.listOfOperators = testTraces.operators
		
		if 'prop' in self.listOfOperators:
			self.listOfOperators.remove('prop')
			
		
		self.unaryOperators = [op for op in self.listOfOperators if op in unary]
		self.binaryOperators = [op for op in self.listOfOperators if op in binary]
		
		#self.noneOperator = 'none' # a none operator is not needed in this encoding
		
		self.solver = Solver()
		self.formula_size = size
		self.fr = fr
		self.traces = testTraces
		self.interestingTP = interestingPoints
		self.numTP = len(self.interestingTP)

		self.listOfPropositions = [i for i in range(self.traces.numPropositions)]
		
	   
	"""	
	the working variables are 
		- x[i][o]: i is a subformula (row) identifier, o is an operator or a propositional variable. Meaning is "subformula i is an operator (variable) o"
		- l[i][j]:  "left operand of subformula i is subformula j"
		- r[i][j]: "right operand of subformula i is subformula j"
		- y[i][tr][t]: semantics of formula i in time point t of trace tr
	"""
	def encodeFormula(self, unsatCore=True):
		

		self.operatorsAndPropositions = self.listOfOperators + self.listOfPropositions
		
		self.x = { (i, o) : Bool('x_%d_%d'%(i,o)) for i in range(self.formula_size) for o in self.operatorsAndPropositions }
		
		self.l = {(parentOperator, childOperator) : Bool('l_%d_%d'%(parentOperator,childOperator))\
												 for parentOperator in range(1, self.formula_size)\
												 for childOperator in range(parentOperator)}
		self.r = {(parentOperator, childOperator) : Bool('r_%d_%d'%(parentOperator,childOperator))\
												 for parentOperator in range(1, self.formula_size)\
												 for childOperator in range(parentOperator)}

		self.y = { (i, traceIdx, positionInTrace) : Bool('y_%d_%d_%d'%(i,traceIdx,positionInTrace))\
				  for i in range(self.formula_size)\
				  for traceIdx, trace in enumerate(self.traces.acceptedTraces + self.traces.rejectedTraces)\
				  for positionInTrace in range(trace.lengthOfTrace)}
		
	   	self.f  = {i: Real('f_%d'%i) for i in range(self.formula_size) }


	   	self.a = {i: Int('a_%d'%i) for i in range(self.formula_size)}
	   	self.b = {i: Int('a_%d'%i) for i in range(self.formula_size)}




		self.solver.set(unsat_core=unsatCore)

		# Structural Constriants
		self.exactlyOneOperator()	   
		self.firstOperatorProposition()
		self.noDanglingPropositions()

		self.temporalBoundsRelation() #<---
		
		self.propositionsSemantics() 
		self.operatorsSemantics() #<---

		self.futureReachBound() #<---
		
		self.solver.assert_and_track(And( [ self.y[(self.formula_size - 1, traceIdx, 0)] for traceIdx in range(len(self.traces.acceptedTraces))] ), 'accepted traces should be accepting')
		self.solver.assert_and_track(And( [ Not(self.y[(self.formula_size - 1, traceIdx, 0)]) for traceIdx in range(len(self.traces.acceptedTraces), len(self.traces.acceptedTraces+self.traces.rejectedTraces))] ),\
									 'rejecting traces should be rejected')


	def futureReachBound(self):	

		for i in range(self.formula_size):	
				
			for p in self.listOfPropositions: 

				self.solver.assert_and_track(Implies(self.x[(i, p)], self.f[i] == 0.0),\
														 'future reach of proposition %s for node %d'%(p,i))

			if '|' in self.listOfOperators:
				
				#disjunction
				self.solver.assert_and_track(Implies(self.x[(i, '|')],\
														And([ Implies(\
																	   And(\
																		   [self.l[i, leftArg], self.r[i, rightArg]]\
																		   ),\
																	   self.f[i] = max(self.f[leftArg], self.f[rightArg])
																	   )\
																	  for leftArg in range(i) for rightArg in range(i) ])),\
														 'future reach of disjunction for node %d'%i)
			if '&' in self.listOfOperators:
				
				#conjunction
				self.solver.assert_and_track(Implies(self.x[(i, '&')],\
														And([ Implies(\
																	   And(\
																		   [self.l[i, leftArg], self.r[i, rightArg]]\
																		   ),\
																	   self.f[i] = max(self.f[leftArg], self.f[rightArg])
																	   )\
																	  for leftArg in range(i) for rightArg in range(i) ])),\
														 'future reach of conjunction for node %d'%(traceIdx, i))
				 
			if '->' in self.listOfOperators:
				   
				#implication
				self.solver.assert_and_track(Implies(self.x[(i, '->')],\
														And([ Implies(\
																	   And(\
																		   [self.l[i, leftArg], self.r[i, rightArg]]\
																		   ),\
																	   self.f[i] = max(self.f[leftArg], self.f[rightArg])
																	   )\
																	  for leftArg in range(i) for rightArg in range(i) ])),\
														 'future reach of implication for node %d'%(traceIdx, i))
			if '!' in self.listOfOperators:
				  #negation
				self.solver.assert_and_track(Implies(self.x[(i, '!')],\
													   And([\
														   Implies(\
																	 self.l[(i,onlyArg)],\
																	 self.f[i] = self.f[onlyArg]
																	  )\
														   for onlyArg in range(i)\
														   ])\
													   ),\
											   'future reach of negation for node %d' % (traceIdx, i)\
											   )
			if 'G' in self.listOfOperators:
				  #globally				
				self.solver.assert_and_track(Implies(self.x[(i, 'G')],\
													   And([\
														   Implies(\
																	 self.l[(i,onlyArg)],\
																	 self.f[i] = sum([If(self.b[i] == j, self.interestingTP[j], 0) for j in self.numTP]) + self.f[onlyArg]
																	  )\
														   for onlyArg in range(i)\
														   ])\
													   ),\
											   'future reach of globally operator for node %d' % (traceIdx, i)\
											   )

			if 'F' in self.listOfOperators:				  
				#finally				
				self.solver.assert_and_track(Implies(self.x[(i, 'F')],\
													   And([\
														   Implies(\
																	 self.l[(i,onlyArg)],\
																	self.f[i] = sum([If(self.b[i] == j, self.interestingTP[j], 0) for j in self.numTP]) + self.f[onlyArg]
																	  )\
														   for onlyArg in range(i)\
														   ])\
													   ),\
											   'future reach of finally operator for node %d'%i)
											   
			  
	def temporalBoundsRelation(self):

		for i in range(self.formula_size):

			if 'G' in self.listOfOperators:
				  #globally				
				self.solver.assert_and_track(Implies(self.x[(i, 'G')], self.a[i] <= self.b[i]),\
											'temporal bounds of globally operator for node %d'%i)

			if 'F' in self.listOfOperators:				  
				  #finally				
				self.solver.assert_and_track(Implies(self.x[(i, 'F')], self.a[i] <= self.b[i]),\
											   'temporal bounds of finally operator for node %d'%i)
											 


	def firstOperatorProposition(self):
		self.solver.assert_and_track(Or([self.x[k] for k in self.x if k[0] == 0 and k[1] in self.listOfPropositions]),\
									 'first operator a variable')

	def noDanglingPropositions(self):
		if self.formula_size > 0:
			self.solver.assert_and_track(
				And([
					Or(
						AtLeast([self.l[(rowId, i)] for rowId in range(i+1, self.formula_size)]+ [1]),
						AtLeast([self.r[(rowId, i)] for rowId in range(i+1, self.formula_size)] + [1])
					)
					for i in range(self.formula_size - 1)]
				),
				"no dangling variables"
			)

	def propositionsSemantics(self):
		for i in range(self.formula_size):
			for p in self.listOfPropositions:
				for traceIdx, tr in enumerate(self.traces.acceptedTraces + self.traces.rejectedTraces):
					self.solver.assert_and_track(Implies(self.x[(i, p)],\
														  And([ self.y[(i,traceIdx, timestep)] if tr.traceVector[timestep][p] == True else Not(self.y[(i, traceIdx, timestep)])\
															   for timestep in range(tr.lengthOfTrace)])),\
														  "semantics of propositional variable node_"+str(i)+' var _'+str(p)+'_trace_'+str(traceIdx))
		
   def exactlyOneOperator(self):
				
			self.solver.assert_and_track(And([\
											  AtMost( [self.x[k] for k in self.x if k[0] == i] +[1])\
											  for i in range(self.formula_size)\
											  ]),\
											  "at most one operator per subformula"\
			)
			
			self.solver.assert_and_track(And([\
											  AtLeast( [self.x[k] for k in self.x if k[0] == i] +[1])\
											  for i in range(self.formula_size)\
											  ]),\
											  "at least one operator per subformula"\
			)
			
			if (self.formula_size > 0):
				self.solver.assert_and_track(And([\
												Implies(
													Or(
														[self.x[(i, op)] for op in self.binaryOperators+self.unaryOperators]
													),
													AtMost( [self.l[k] for k in self.l if k[0] == i] +[1])\
					)
											  for i in range(1,self.formula_size)\
											  ]),\
											  "at most one left operator for binary and unary operators"\
			)
			
			if (self.formula_size > 0):
				self.solver.assert_and_track(And([\
												Implies(
													Or(
														[self.x[(i, op)] for op in
														 self.binaryOperators + self.unaryOperators]
													),
													AtLeast( [self.l[k] for k in self.l if k[0] == i] +[1])\
													)
											  for i in range(1,self.formula_size)\
											  ]),\
											  "at least one left operator for binary and unary operators"\
			)

			if (self.formula_size > 0):
				self.solver.assert_and_track(And([ \
					Implies(
						Or(
							[self.x[(i, op)] for op in self.binaryOperators]
						),
						AtMost([self.r[k] for k in self.r if k[0] == i] + [1]) \
						)
					for i in range(1, self.formula_size) \
					]), \
					"at most one right operator for binary" \
					)

			if (self.formula_size > 0):
				self.solver.assert_and_track(And([ \
					Implies(
						Or(
							[self.x[(i, op)] for op in
							 self.binaryOperators]
						),
						AtLeast([self.r[k] for k in self.r if k[0] == i] + [1]) \
						)
					for i in range(1, self.formula_size) \
					]), \
					"at least one right operator for binary" \
					)

			if (self.formula_size > 0):
				self.solver.assert_and_track(And([ \
					Implies(	
						Or(
							[self.x[(i, op)] for op in
							 self.unaryOperators]
						),
						Not(
							Or([self.r[k] for k in self.r if k[0] == i]) \
						)
					)
					for i in range(1, self.formula_size) \
					]), \
					"no right operators for unary" \
					)

			if (self.formula_size > 0):
				self.solver.assert_and_track(And([ \
					Implies(
						Or(
							[self.x[(i, op)] for op in
							 self.listOfPropositions]
						),
						Not(
							Or(
								Or([self.r[k] for k in self.r if k[0] == i]), \
								Or([self.l[k] for k in self.l if k[0] == i])
							)

						)
					)
					for i in range(1, self.formula_size) \
					]), \
					"no left or right children for variables" \
					)
	

	def operatorsSemantics(self):

		for traceIdx, tr in enumerate(self.traces.acceptedTraces + self.traces.rejectedTraces):
			
			for i in range(1, self.formula_size):	
				
				if '|' in self.listOfOperators:

					T = tr.lengthOfTrace
					#disjunction
					self.solver.assert_and_track(Implies(self.x[(i, '|')],\
															And([ Implies(\
																		   And(\
																			   [self.l[i, leftArg], self.r[i, rightArg]]\
																			   ),\
																		   And(\
																			   [ self.y[(i, traceIdx, timestep)]\
																				==\
																				Or(\
																				   [ self.y[(leftArg, traceIdx, timestep)],\
																					self.y[(rightArg, traceIdx, timestep)]]\
																				   )\
																				 for timestep in range(T)]\
																			   )\
																		   )\
																		  for leftArg in range(i) for rightArg in range(i) ])),\
															 'semantics of disjunction for trace %d and node %d'%(traceIdx, i))
				if '&' in self.listOfOperators:
					#conjunction
					self.solver.assert_and_track(Implies(self.x[(i, '&')],\
															And([ Implies(\
																		   And(\
																			   [self.l[i, leftArg], self.r[i, rightArg]]\
																			   ),\
																		   And(\
																			   [ self.y[(i, traceIdx, timestep)]\
																				==\
																				And(\
																				   [ self.y[(leftArg, traceIdx, timestep)],\
																					self.y[(rightArg, traceIdx, timestep)]]\
																				   )\
																				 for timestep in range(T)]\
																			   )\
																		   )\
																		  for leftArg in range(i) for rightArg in range(i) ])),\
															 'semantics of conjunction for trace %d and node %d'%(traceIdx, i))
					 
				if '->' in self.listOfOperators:
					   
					#implication
					self.solver.assert_and_track(Implies(self.x[(i, '->')],\
															And([ Implies(\
																		   And(\
																			   [self.l[i, leftArg], self.r[i, rightArg]]\
																			   ),\
																		   And(\
																			   [ self.y[(i, traceIdx, timestep)]\
																				==\
																				Implies(\
																				  self.y[(leftArg, traceIdx, timestep)],\
																				  self.y[(rightArg, traceIdx, timestep)]\
																				   )\
																				 for timestep in range(T)]\
																			   )\
																		   )\
																		  for leftArg in range(i) for rightArg in range(i) ])),\
															 'semantics of implication for trace %d and node %d'%(traceIdx, i))

				if '!' in self.listOfOperators:
					#negation
					self.solver.assert_and_track(Implies(self.x[(i, '!')],\
														   And([\
															   Implies(\
																		 self.l[(i,onlyArg)],\
																		 And([\
																			  self.y[(i, traceIdx, timestep)] == Not(self.y[(onlyArg, traceIdx, timestep)])\
																			  for timestep in range(T)\
																			  ])\
																		  )\
															   for onlyArg in range(i)\
															   ])\
														   ),\
												   'semantics of negation for trace %d and node %d' % (traceIdx, i)\
												   )
				if 'G' in self.listOfOperators:
					#globally				
					self.solver.assert_and_track(Implies(self.x[(i, 'G')],\
														   And([\
															   Implies(\
																		 self.l[(i,onlyArg)],\
																		 And([\
																			  self.y[(i, traceIdx, timestep)] ==\
																			  And(timestep+self.a[i] <  )


																			  And([self.y[(onlyArg, traceIdx, futureTimestep)] for futureTimestep in range(timestep, tr.lengthOfTrace) ])\
																			  for timestep in range(T)\
																			  ])\
																		  )\
															   for onlyArg in range(i)\
															   ])\
														   ),\
												   'semantics of globally operator for trace %d and node %d' % (traceIdx, i)\
												   )

				if 'F' in self.listOfOperators:				  
					  #finally				
					self.solver.assert_and_track(Implies(self.x[(i, 'F')],\
														   And([\
															   Implies(\
																		 self.l[(i,onlyArg)],\
																		 And([\
																			  self.y[(i, traceIdx, timestep)] ==\
																			  Or([self.y[(onlyArg, traceIdx, futureTimestep)] for futureTimestep in range(timestep, tr.lengthOfTrace) ])\
																			  for timestep in range(T)\
																			  ])\
																		  )\
															   for onlyArg in range(i)\
															   ])\
														   ),\
												   'semantics of finally operator for trace %d and node %d' % (traceIdx, i)\
												   )
				  
				
	

	def reconstructWholeFormula(self, model):
		return self.reconstructFormula(self.formula_size-1, model)   
		
	def reconstructFormula(self, rowId, model):
		def getValue(row, vars):
			tt = [k[1] for k in vars if k[0] == row and model[vars[k]] == True]
			if len(tt) > 1:
				raise Exception("more than one true value")
			else:
				return tt[0]
		operator = getValue(rowId, self.x)
		if operator in self.listOfPropositions:
			return Formula('x'+str(operator))
		elif operator in self.unaryOperators:
			leftChild = getValue(rowId, self.l)
			return Formula([operator, self.reconstructFormula(leftChild, model)])
		elif operator in self.binaryOperators:
			leftChild = getValue(rowId, self.l)
			rightChild = getValue(rowId, self.r)
			return Formula([operator, self.reconstructFormula(leftChild,model), self.reconstructFormula(rightChild, model)])
		

def main()

	sample = Sample()
	sample.readSample(signalfile)
	wordsamplefile = signalfile.split('.')[0]+'.trace'
	
	wordsample, alphabet, interval_map, prop2pred, start_time, end_time = convertSignals2Traces(sample, wordsamplefile, ['F', 'X', '&', '|', '!'])





