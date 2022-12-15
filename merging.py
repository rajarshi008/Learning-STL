from z3 import *


class SMTEncoding:

	def __init__(self):

		self.max_intervals = 10
		self.start_time = 0
		self.end_time = 20

		self.solver = Solver()

		

	def def_vars(self):
		# 0, 3, 4, 9
		self.initial_tp1 = [0, 2, 5, 6, 7, 9, 10, 10, 10]
		self.initial_tp2 = [0, 1, 3, 4, 8, 9, 10, 10, 10]
		self.max_intervals = len(self.initial_tp1)
		self.start_time = self.initial_tp1[0]
		self.end_time = self.initial_tp1[-1]

		self.s1 = {i:Real('s1_%d'%i) for i in range(1,self.max_intervals+1)}#dummy variables
		self.s2 = {i:Real('s2_%d'%i) for i in range(1,self.max_intervals+1)}#dummy variables
		self.t = {i:Real('t_%d'%i)for i in range(1,self.max_intervals+1)}#actual variables
		self.num_tp = Int('r')

		#Checking on some examples
		initial_cons = And([And(self.s1[i] == self.initial_tp1[i-1], self.s2[i] == self.initial_tp2[i-1]) for i in range(1,self.max_intervals+1)])
		self.solver.assert_and_track(initial_cons, 'Inital timepoints')

		if self.max_intervals%2 != 0:
			self.even_range = int((self.max_intervals-1)/2)
			self.odd_range = int((self.max_intervals+1)/2)
		else:
			self.even_range = int((self.max_intervals)/2)
			self.odd_range = int((self.max_intervals)/2)

	def constraints_for_F(self):
		
		#[0,6,7,10, 11, 12, 20,20,20]

		interval_bound = And(1<self.num_tp, self.num_tp<=self.max_intervals)
		self.solver.assert_and_track(interval_bound, 'Bound for number of relevant time points')

		end_point_bound = And([Implies(i>=self.num_tp, self.t[i] == self.end_time) \
								for i in range(1,self.max_intervals+1)])
		self.solver.assert_and_track(end_point_bound, 'End time points')

		
		cons1 = And([Or([Implies(2*i<=self.num_tp,self.t[2*i] == self.s1[2*j]) \
						for j in range(1, even_range+1)]) \
						for i in range(1, even_range+1)])
		self.solver.assert_and_track(cons1, 'Even variables are set to one of the even dummy variables')

		cons2 = And([Or([Implies(2*i-1<=self.num_tp, self.t[2*i-1] == self.s1[2*j-1]) \
						for j in range(1, odd_range+1)]) \
						for i in range(1, odd_range+1)])
		self.solver.assert_and_track(cons2 , 'Odd variables are set to one of the odd dummy variables')
		
		#cons = And([Or([self.t[i] == self.s1[j] \
		#				for j in range(1, self.max_intervals+1)]) \
		#				for i in range(1, self.max_intervals+1)])
		#self.solver.assert_and_track(cons , 'Actual variables are set to one of the dummy variables')

		cons3 = And([Implies(i<self.num_tp, self.t[i]<self.t[i+1]) \
						for i in range(1,self.max_intervals)])
		self.solver.assert_and_track(cons3 , 'Maintain order between variables')	
		
		cons4 = And([Or([And(self.t[2*j-1]<=self.s1[2*i-1], self.s1[2*i]<=self.t[2*j]) \
							for j in range(1, even_range+1)]) \
							for i in range(1, even_range+1)])
		self.solver.assert_and_track(cons4 , 'All intervals must be included')


		cons5 = And([Implies(self.s1[2*i]<self.s1[2*j-1], \
					Implies(And([Or((self.s1[2*i]+self.s1[2*j-1])/2<self.s1[2*k-1], (self.s1[2*i]+self.s1[2*j-1])/2>self.s1[2*k]) \
						for k in range(1, even_range)]),\
						And([Or((self.s1[2*i]+self.s1[2*j-1])/2<self.t[2*l-1], (self.s1[2*i]+self.s1[2*j-1])/2>self.t[2*l]) for l in range(1,even_range)])
						))\
					for i in range(1, even_range+1) for j in range(1, odd_range+1)])
		self.solver.assert_and_track(cons5 , 'No extra variables should be included')

		
	def constraints_for_or_old(self):

		interval_bound = And(1<self.num_tp, self.num_tp<=self.max_intervals)
		self.solver.assert_and_track(interval_bound, 'Bound for number of relevant time points')

		end_point_bound = And([Implies(i>=self.num_tp, self.t[i] == self.end_time) \
								for i in range(1,self.max_intervals+1)])
		self.solver.assert_and_track(end_point_bound, 'End time points')
		
		cons1 = And([Or([Implies(2*i<=self.num_tp,Or(self.t[2*i] == self.s1[2*j], self.t[2*i] == self.s2[2*j])) \
						for j in range(1, self.even_range+1)]) \
						for i in range(1, self.even_range+1)])
		self.solver.assert_and_track(cons1, 'Even variables are set to one of the even dummy variables')

		cons2 = And([Or([Implies(2*i-1<=self.num_tp, Or(self.t[2*i-1] == self.s1[2*j-1], self.t[2*i-1] == self.s2[2*j-1])) \
						for j in range(1, self.odd_range+1)]) \
						for i in range(1, self.odd_range+1)])
		self.solver.assert_and_track(cons2 , 'Odd variables are set to one of the odd dummy variables')

		
		cons3 = And([Implies(i<self.num_tp, self.t[i]<self.t[i+1]) \
						for i in range(1,self.max_intervals)])
		self.solver.assert_and_track(cons3 , 'Maintain order between variables')
		
		
		cons4 = And([Implies((self.t[2*i-1]==self.s1[2*j-1]), \
						And([Or(self.s1[2*j-1]<=self.s2[2*k-1], self.s2[2*k]<=self.s1[2*j-1]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.odd_range+1) for i in range(1, self.odd_range+1)])
		self.solver.assert_and_track(cons4, 'Odd variables should be correct for s1 variables')

		cons5 = And([Implies((self.t[2*i]==self.s1[2*j]), \
						And([Or(self.s1[2*j]<=self.s2[2*k-1], self.s2[2*k]<=self.s1[2*j]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.even_range+1) for i in range(1, self.even_range+1)])
		self.solver.assert_and_track(cons5, 'Even variables should be correct for s1 variables')

		print(self.odd_range, self.even_range)
		cons6 = And([Implies((self.t[2*i-1]==self.s2[2*j-1]), \
						And([Or(self.s2[2*j-1]<=self.s1[2*k-1], self.s1[2*k]<=self.s2[2*j-1]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.odd_range+1) for i in range(1, self.odd_range+1)])
		self.solver.assert_and_track(cons6, 'Odd variables should be correct for s2 variables')

		cons7 = And([Implies((self.t[2*i]==self.s2[2*j]), \
						And([Or(self.s2[2*j]<=self.s1[2*k-1], self.s1[2*k]<=self.s2[2*j]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.even_range+1) for i in range(1, self.even_range+1)])
		self.solver.assert_and_track(cons7, 'Even variables should be correct for s2 variables')


	def constraints_for_or(self):

		interval_bound = And(1<self.num_tp, self.num_tp<=self.max_intervals)
		self.solver.assert_and_track(interval_bound, 'Bound for number of relevant time points')

		end_point_bound = And([Implies(i>=self.num_tp, self.t[i] == self.end_time) \
								for i in range(1,self.max_intervals+1)])
		self.solver.assert_and_track(end_point_bound, 'End time points')
		
		cons1 = And([Or([Implies(i<=self.num_tp,Or(self.t[i] == self.s1[j], self.t[i] == self.s2[j])) \
						for j in range(2, self.max_intervals+1, 2)]) \
						for i in range(2, self.max_intervals+1, 2)])
		self.solver.assert_and_track(cons1, 'Even variables are set to one of the even dummy variables')

		cons2 = And([Or([Implies(2*i-1<=self.num_tp, Or(self.t[2*i-1] == self.s1[2*j-1], self.t[2*i-1] == self.s2[2*j-1])) \
						for j in range(1, self.odd_range+1)]) \
						for i in range(1, self.odd_range+1)])
		self.solver.assert_and_track(cons2 , 'Odd variables are set to one of the odd dummy variables')

		
		cons3 = And([Implies(i<self.num_tp, self.t[i]<self.t[i+1]) \
						for i in range(1,self.max_intervals)])
		self.solver.assert_and_track(cons3 , 'Maintain order between variables')
		
		
		cons4 = And([Implies((self.t[2*i-1]==self.s1[2*j-1]), \
						And([Or(self.s1[2*j-1]<=self.s2[2*k-1], self.s2[2*k]<=self.s1[2*j-1]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.odd_range+1) for i in range(1, self.odd_range+1)])
		self.solver.assert_and_track(cons4, 'Odd variables should be correct for s1 variables')

		cons5 = And([Implies((self.t[2*i]==self.s1[2*j]), \
						And([Or(self.s1[2*j]<=self.s2[2*k-1], self.s2[2*k]<=self.s1[2*j]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.even_range+1) for i in range(1, self.even_range+1)])
		self.solver.assert_and_track(cons5, 'Even variables should be correct for s1 variables')

		print(self.odd_range, self.even_range)
		cons6 = And([Implies((self.t[2*i-1]==self.s2[2*j-1]), \
						And([Or(self.s2[2*j-1]<=self.s1[2*k-1], self.s1[2*k]<=self.s2[2*j-1]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.odd_range+1) for i in range(1, self.odd_range+1)])
		self.solver.assert_and_track(cons6, 'Odd variables should be correct for s2 variables')

		cons7 = And([Implies((self.t[2*i]==self.s2[2*j]), \
						And([Or(self.s2[2*j]<=self.s1[2*k-1], self.s1[2*k]<=self.s2[2*j]) for k in range(1, self.even_range+1)]))
						for j in range(1, self.even_range+1) for i in range(1, self.even_range+1)])
		self.solver.assert_and_track(cons7, 'Even variables should be correct for s2 variables')


# interval = {i:(Real('l_i'), Real('r_i') for i in range()}


	def find_sol(self):

		solverRes = self.solver.check()

		if solverRes == sat:
			solverModel = self.solver.model()
			print('SAT')
			for k in self.t:
				print('t_%d'%k, solverModel[self.t[k]])
			print('Num TP', solverModel[self.num_tp])
		else:
			checking= self.solver.unsat_core()
			print(checking)
			print('UNSAT')
	

	def ensureProperIntervals(self, itvs, end_time):

		cons1 = And([itvs[i][0]<=itvs[i][1] for i in itvs])
		self.solver.add(cons1)

		cons2 = And([itvs[i][1]<=itvs[i+1][0] for i in range(len(itvs)-1)])
		self.solver.add(cons2)

		cons3 = And([And(0<=itvs[i][s], itvs[i][s]<=end_time) for s in [0,1] for i in range(len(itvs))])
		self.solver.add(cons3)


	def negation_itv(self, itvs, neg_itvs, old_num_itv, new_num_itv, end_time):

		case1 = And([And(neg_itvs[0][0]==0, neg_itvs[0][1]==itvs[0][0])]+\
						[Implies(i<=old_num_itv,And(neg_itvs[i][0] == itvs[i-1][1], neg_itvs[i][1] == itvs[i][0])) for i in range(1,len(itvs))])
		case2 = And([Implies(i<=old_num_itv,And(neg_itvs[i][0]==itvs[i][1], neg_itvs[i][1]==itvs[i+1][0])) for i in range(len(itvs)-1)])
		
		self.solver.add(If(itvs[0][0] != 0, case1, case2))

		self.solver.add(And([Implies(And(neg_itvs[i][0]==end_time, neg_itvs[i-1][0]!=end_time), new_num_itv==i) for i in range(1,len(itvs))]))
		


	def checking(self):

		actual_itv1 = [(2,3),(4,6),(7,8),(9,9),(9,9)]

		itv1 = {i:(Real('itv1_%d_0'%i), Real('itv1_%d_1'%i)) for i in range(len(actual_itv1))}
		itv2 = {i:(Real('itv2_%d_0'%i), Real('itv2_%d_1'%i)) for i in range(len(actual_itv1))}
		num_itv = Real('num_itv')
		new_num_itv = Real('num_itv_1')

		self.solver.add(And([And(itv1[i][0]==actual_itv1[i][0], itv1[i][1]==actual_itv1[i][1]) for i in range(len(actual_itv1))]+[num_itv==3]))
		self.ensureProperIntervals(itv2, 9)
		self.negation_itv(itv1, itv2, num_itv, new_num_itv, 9)


		solverRes = self.solver.check()

		if solverRes == sat:
			solverModel = self.solver.model()
			for i in range(len(actual_itv1)):
				print((solverModel[itv2[i][0]],solverModel[itv2[i][1]]))
			print(solverModel[new_num_itv])

def main():

	s = SMTEncoding()
	s.checking()
	#
	#s.def_vars()
	#s.constraints_for_or()
	#s.find_sol()

main()


