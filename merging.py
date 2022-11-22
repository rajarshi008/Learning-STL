from z3 import *


class SMTEncoding:

	def __init__(self):

		self.max_intervals = 9
		self.start_time = 0
		self.end_time = 20

		self.solver = Solver()

	def def_vars(self):

		self.s = {i:Real('t_%d'%i) for i in range(1,self.max_intervals+1)}#dummy variables
		self.t = {i:Real('t_%d'%i)for i in range(1,self.max_intervals+1)}#actual variables
		self.num_tp = Int('r')

	def constraints(self):

		initial_tp = [0, 4, 2, 6, 7, 10, 9, 11, 20]
		#[0,6,7,11,20]

		self.solver.assert_and_track(And([self.s[i] == initial_tp[i-1] for i in range(1,self.max_intervals+1)]), 'Inital timepoints')

		if self.max_intervals%2 != 0:
			even_range = int((self.max_intervals-1)/2)
			odd_range = int((self.max_intervals+1)/2)
		else:
			even_range = int((self.max_intervals)/2)
			odd_range = int((self.max_intervals)/2)


		interval_bound = And(1<=self.num_tp, self.num_tp<=self.max_intervals)
		self.solver.assert_and_track(interval_bound, 'Bound for number of relevant time points')

		cons1 = And([Or([self.t[2*i] == self.s[2*j] \
						for j in range(1, even_range+1)]) \
						for i in range(1, even_range+1)])
		self.solver.assert_and_track(cons1, 'Even variables are set to one of the even dummy variables')

		cons2 = And([Or([self.t[2*i-1] == self.s[2*j-1] \
						for j in range(1, odd_range+1)]) \
						for i in range(1, odd_range+1)])
		self.solver.assert_and_track(cons2 , 'Odd variables are set to one of the odd dummy variables')

		cons3 = And([self.t[i]<self.t[i+1] \
						for i in range(1,self.max_intervals)])
		self.solver.assert_and_track(cons3 , 'Maintain order between variables')	

		cons4 = And([Or([And(self.t[j]<=self.s[i], self.s[i]<=self.t[j+1]) \
							for j in range(1, self.max_intervals)]) \
							for i in range(1, self.max_intervals+1)])
		self.solver.assert_and_track(cons4 , 'All dummy variables should be included')


		cons5 = And([Implies(self.s[2*i]<self.s[2*j-1], \
					Implies(And([Or((self.s[2*i]+self.s[2*j-1])/2<self.s[k], (self.s[2*i]+self.s[2*j-1])/2>self.s[k+1]) \
						for k in range(1, self.max_intervals)]),\
						And([Or((self.s[2*i]+self.s[2*j-1])/2<self.t[l], (self.s[2*i]+self.s[2*j-1])/2>self.t[l+1]) for l in range(1,self.max_intervals)])
						)\
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

			print('UNSAT')
	



def main():

	s = SMTEncoding()
	s.def_vars()
	s.constraints()
	s.find_sol()

main()