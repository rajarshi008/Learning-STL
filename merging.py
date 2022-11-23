from z3 import *


class SMTEncoding:

	def __init__(self):

		self.max_intervals = 10
		self.start_time = 0
		self.end_time = 20

		self.solver = Solver()

	def def_vars(self):

		self.initial_tp = [0, 4, 2, 7, 6, 10, 9, 12, 20, 20, 20]
		self.max_intervals = len(self.initial_tp)
		self.start_time = self.initial_tp[0]
		self.end_time = self.initial_tp[-1]

		self.s = {i:Real('s_%d'%i) for i in range(1,self.max_intervals+1)}#dummy variables
		self.t = {i:Real('t_%d'%i)for i in range(1,self.max_intervals+1)}#actual variables
		self.num_tp = Int('r')

	def constraints(self):

		
		#[0,6,7,10, 11, 12, 20,20,20]

		
		if self.max_intervals%2 != 0:
			even_range = int((self.max_intervals-1)/2)
			odd_range = int((self.max_intervals+1)/2)
		else:
			even_range = int((self.max_intervals)/2)
			odd_range = int((self.max_intervals)/2)

		initial_cons = And([self.s[i] == self.initial_tp[i-1] for i in range(1,self.max_intervals+1)])
		self.solver.assert_and_track(initial_cons, 'Inital timepoints')


		interval_bound = And(1<self.num_tp, self.num_tp<=self.max_intervals)
		self.solver.assert_and_track(interval_bound, 'Bound for number of relevant time points')

		end_point_bound = And([Implies(i>=self.num_tp, self.t[i] == self.end_time) \
								for i in range(1,self.max_intervals+1)])
		self.solver.assert_and_track(end_point_bound, 'End time points')

		
		cons1 = And([Or([Implies(2*i<=self.num_tp,self.t[2*i] == self.s[2*j]) \
						for j in range(1, even_range+1)]) \
						for i in range(1, even_range+1)])
		self.solver.assert_and_track(cons1, 'Even variables are set to one of the even dummy variables')

		cons2 = And([Or([Implies(2*i-1<=self.num_tp, self.t[2*i-1] == self.s[2*j-1]) \
						for j in range(1, odd_range+1)]) \
						for i in range(1, odd_range+1)])
		self.solver.assert_and_track(cons2 , 'Odd variables are set to one of the odd dummy variables')
		
		#cons = And([Or([self.t[i] == self.s[j] \
		#				for j in range(1, self.max_intervals+1)]) \
		#				for i in range(1, self.max_intervals+1)])
		#self.solver.assert_and_track(cons , 'Actual variables are set to one of the dummy variables')

		cons3 = And([Implies(i<self.num_tp, self.t[i]<self.t[i+1]) \
						for i in range(1,self.max_intervals)])
		self.solver.assert_and_track(cons3 , 'Maintain order between variables')	
		
		cons4 = And([Or([And(self.t[2*j-1]<=self.s[2*i-1], self.s[2*i]<=self.t[2*j]) \
							for j in range(1, even_range+1)]) \
							for i in range(1, even_range+1)])
		self.solver.assert_and_track(cons4 , 'All intervals must be included')


		cons5 = And([Implies(self.s[2*i]<self.s[2*j-1], \
					Implies(And([Or((self.s[2*i]+self.s[2*j-1])/2<self.s[2*k-1], (self.s[2*i]+self.s[2*j-1])/2>self.s[2*k]) \
						for k in range(1, even_range)]),\
						And([Or((self.s[2*i]+self.s[2*j-1])/2<self.t[2*l-1], (self.s[2*i]+self.s[2*j-1])/2>self.t[2*l]) for l in range(1,even_range)])
						)\
					for i in range(1, even_range+1) for j in range(1, odd_range+1)\
					])
		self.solver.assert_and_track(cons5 , 'No extra variables should be included')
		


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
	



def main():

	s = SMTEncoding()
	s.def_vars()
	s.constraints()
	s.find_sol()

main()