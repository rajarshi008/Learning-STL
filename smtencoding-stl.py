from z3 import *
from formula import STLFormula


class SMTEncoding:

	def __init__(self, traces, formula_size, alphabet, itp, utp, prop2pred): 
		
		defaultOperators = ['G', 'F', '!', '&', '|', '->']
		unary = ['G','F', '!']	
		binary = ['&', '|', '->']
		

		#unary = ['G']	
		#binary = ['&']
		#defaultOperators = ['G', 'F']
		#unary = ['G', 'F']	
		#binary = []
		
		#except for the operators, the nodes of the "syntaxDAG" are additionally the propositional variables 
		
		'''
		if testTraces.operators == None:
			self.listOfOperators = defaultOperators
		else:
			self.listOfOperators = testTraces.operators
		
		if 'prop' in self.listOfOperators:
			self.listOfOperators.remove('prop')
			
		'''
		self.unaryOperators = unary
		self.binaryOperators = binary
		self.listOfOperators = self.unaryOperators + self.binaryOperators

		#self.noneOperator = 'none' # a none operator is not needed in this encoding
		
		self.solver = Solver()
		self.formula_size = formula_size
		self.traces = traces
		self.alphabet = alphabet
		self.itp = itp
		self.utp = utp
		self.numtp = len(self.itp)
		self.listOfPropositions = list(range(len(alphabet)))
		self.prop2pred = prop2pred

		#self.listOfPropositions = [i for i in range(self.traces.numPropositions)]
		
	   
	"""	
	the working variables are 
		- x[i][o]: i is a subformula (row) identifier, o is an operator or a propositional variable. Meaning is "subformula i is an operator (variable) o"
		- l[i][j]:  "left operand of subformula i is subformula j"
		- r[i][j]: "right operand of subformula i is subformula j"
		- y[i][tr][t]: semantics of formula i in time point t of trace tr
	"""
	def encodeFormula(self, unsatCore=True):
		

		self.operatorsAndPropositions = self.listOfOperators + self.listOfPropositions
		print(self.operatorsAndPropositions)
		
		self.x = { (i, o) : Bool('x_%d_%s'%(i,o)) for i in range(self.formula_size) for o in self.operatorsAndPropositions}
		
		self.a = {i: Real('a_%d'%i) for i in range(self.formula_size)}
	
		self.b = {i: Real('b_%d'%i) for i in range(self.formula_size)}


		self.l = {(parentOperator, childOperator) : Bool('l_%d_%d'%(parentOperator,childOperator))\
												 for parentOperator in range(1,self.formula_size)\
												 for childOperator in range(parentOperator)} 
		
		self.r = {(parentOperator, childOperator) : Bool('r_%d_%d'%(parentOperator,childOperator))\
												 for parentOperator in range(1,self.formula_size)\
												 for childOperator in range(parentOperator)}

		self.y = { (i, traceIdx, pos) : Bool('y_%d_%d_%d'%(i,traceIdx,pos))\
				  for i in range(self.formula_size)\
				  for traceIdx, trace in enumerate(self.traces.positive + self.traces.negative)\
				  for pos in range(len(self.utp)) }
		
		#print('x-vars:',self.x)
		#print('y-vars',self.y)
		#print('l-vars:',self.l)
		self.solver.set()

		# Structural Constraints
		self.exactlyOneOperator()	   
		self.firstOperatorProposition()
		self.noDanglingPropositions()
		self.temporalBoundsRelation() #<---
		
		# Semantic Constraints
		self.propositionsSemantics()
		self.operatorsSemantics() #<---

		#self.futureReachBound() #<---
		for traceIdx in range(len(self.traces.positive)):
			self.solver.add(self.y[(self.formula_size - 1, traceIdx, 0)])
					

		for traceIdx in range(len(self.traces.positive), len(self.traces.positive+self.traces.negative)):
			self.solver.add(Not(self.y[(self.formula_size - 1, traceIdx, 0)]))

		
										   
			  
	def temporalBoundsRelation(self):

		for i in range(self.formula_size):

			if 'G' in self.listOfOperators:
				  #globally				
				self.solver.assert_and_track(Implies(self.x[(i, 'G')], (self.a[i] <= self.b[i])),\
											'temporal bounds of globally operator for node %d'%i)

				self.solver.assert_and_track(Implies(self.x[(i, 'G')], Or([self.a[i] == self.utp[tp] for tp in range(len(self.utp))])),\
											'temporal lower bounds values of globally operator for node %d'%i)
 
				self.solver.assert_and_track(Implies(self.x[(i, 'G')], Or([self.b[i] == self.utp[tp] for tp in range(len(self.utp))])),\
											'temporal upper bounds values of globally operator for node %d'%i)
				#self.solver.assert_and_track(Implies(self.x[(i, 'G')], Or([self.b[i] == 3])),\
				#							'temporal upper bounds values of globally operator for node %d'%i)
 
			if 'F' in self.listOfOperators:				  
				  #finally				
				self.solver.assert_and_track(Implies(self.x[(i, 'F')], (self.a[i] <= self.b[i])),\
											   'temporal bounds of finally operator for node %d'%i)
				
				self.solver.assert_and_track(Implies(self.x[(i, 'F')], Or([self.a[i] == self.utp[tp] for tp in range(len(self.utp))])),\
											'temporal lower bounds values of finally operator for node %d'%i)
 
				self.solver.assert_and_track(Implies(self.x[(i, 'F')], Or([self.b[i] == self.utp[tp] for tp in range(len(self.utp))])),\
											'temporal upper bounds values of finally operator for node %d'%i)						 


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
			#
			for p in self.listOfPropositions:
			#	
				for traceIdx, tr in enumerate(self.traces.positive + self.traces.negative):
				#	
					#print('For trace %d'%traceIdx)
					conjunction_list = []
					itp_pos = 0

					for tp in range(len(self.utp)):
						#print('tp', tp)
						

						if self.utp[tp] == self.itp[itp_pos]:
							itp_pos += 1

						#if tp>=10:
						#	print(self.utp[tp], self.itp[itp_pos-1], tr.vector[itp_pos-1][p])

						conjunction_list.append(self.y[(i,traceIdx, tp)] \
							if tr.vector[itp_pos-1][p] == True else Not(self.y[(i, traceIdx, tp)]))



					self.solver.assert_and_track(Implies(self.x[(i, p)],\
														  And(conjunction_list)),\
														  "semantics of propositional variable node_"\
														  +str(i)+' var _'+str(p)+'_trace_'+str(traceIdx))

		
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

		for traceIdx, tr in enumerate(self.traces.positive + self.traces.negative):
			
			for i in range(1, self.formula_size):

				T = len(self.utp)
				if '|' in self.listOfOperators:

					#disjunction
					self.solver.assert_and_track(Implies(self.x[(i, '|')],\
															And([ Implies(\
																		   And(\
																			   [self.l[i, leftArg], self.r[i, rightArg]]\
																			   ),\
																		   And(\
																			   [ self.y[(i, traceIdx, tp)]\
																				==\
																				Or(\
																				   [ self.y[(leftArg, traceIdx, tp)],\
																					self.y[(rightArg, traceIdx, tp)]]\
																				   )\
																				 for tp in range(T)]\
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
																			   [ self.y[(i, traceIdx, tp)]\
																				==\
																				And(\
																				   [ self.y[(leftArg, traceIdx, tp)],\
																					self.y[(rightArg, traceIdx, tp)]]\
																				   )\
																				 for tp in range(T)]\
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
																			   [ self.y[(i, traceIdx, tp)]\
																				==\
																				Implies(\
																				  self.y[(leftArg, traceIdx, tp)],\
																				  self.y[(rightArg, traceIdx, tp)]\
																				   )\
																				 for tp in range(T)]\
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
																			  self.y[(i, traceIdx, tp)] == Not(self.y[(onlyArg, traceIdx, tp)])\
																			  for tp in range(T)\
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
																		 self.l[(i,j)],\
																		 And([\
																			  self.y[(i, traceIdx, tp)] ==\
																			  And(\
																			  	[Implies(And((self.utp[tp]+self.a[i]<=self.utp[tp1]),\
																			  		(self.utp[tp1]<=self.utp[tp]+self.b[i])), self.y[j, traceIdx, tp1]) \
																			  	for tp1 in range(tp,T)])\
																			  for tp in range(T)]))\
															   for j in range(i)\
															   ])\
														   ),\
												   'semantics of globally operator for trace %d and node %d' % (traceIdx, i)\
												   )

				if 'F' in self.listOfOperators:				  
					#finally				
					self.solver.assert_and_track(Implies(self.x[(i, 'F')],\
														   And([\
															   Implies(\
																		 self.l[(i,j)],\
																		 And([\
																			  self.y[(i, traceIdx, tp)] ==\
																			  Or(\
																			  	[And([(self.utp[tp]+self.a[i]<=self.utp[tp1]),\
																			  		(self.utp[tp1]<=self.utp[tp]+self.b[i]), self.y[j, traceIdx, tp1]]) \
																			  	for tp1 in range(tp,T)])\
																		  for tp in range(T)]))\
															   for j in range(i)\
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
		
			#print(str(self.alphabet[operator]))
			return STLFormula(label=self.prop2pred[str(self.alphabet[operator])])
		
		elif operator in self.unaryOperators:
		
			leftChild = getValue(rowId, self.l)
			if operator in ['F', 'G']:
				
				lower_bound = model[self.a[rowId]]
				upper_bound = model[self.b[rowId]]
				#print([operator,(lower_bound, upper_bound)])
				return STLFormula(label=[operator,(lower_bound, upper_bound)], left=self.reconstructFormula(leftChild, model)) 
		
			else:
				#print(operator)
				return STLFormula(label=operator, left=self.reconstructFormula(leftChild, model))
		
		elif operator in self.binaryOperators:
			#print(operator)
			leftChild = getValue(rowId, self.l)
			rightChild = getValue(rowId, self.r)
			return STLFormula(label=operator, left=self.reconstructFormula(leftChild,model), right=self.reconstructFormula(rightChild, model))

	'''
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
	'''	  