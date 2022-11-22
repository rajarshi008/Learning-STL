from signaltraces import Signal
from formula import STLFormula 


#To-Do: convert MTL text to formula


mtl_formula = STLFormula(('F',(1,2)), STLFormula('p', None, None), None)
signal_text = [(1.2,1),(2.4,0),(3.2,1),(4,1),(5.2,1),(6,0)]

signal = Signal(sequence=[samplePoint(time=i,vector=[j]) for (i,j) in signal_text])

def monitor(formula, signal):


def truth_signal(formula, signal):

	if formula.left != None: 
		left_signal = truth_signal(formula.left, signal)
	if formula.right != None: 
		right_signal = truth_signal(formula.right, signal)

	if isinstance(formula.label, tuple):
		operator = formula.label[0]
		interval = formula.label[1]

		if operator == 'F':



		if operator == 'G':

	else:
		operator = formula.label

		if operator = '&':





def order_intervals(timepoints: list, truth: bool) -> list:

	if truth:
		new_timepoint = []
		while i< :
			if timepoints[i] <= timepoints[i+2] and timepoints[i+2] <= timepoints[i+1]:
				timepoints[i+1] = max(timepoints[i+1], timepoints[i+3])
				


	else:







