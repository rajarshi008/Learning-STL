


The documentation for this software was created by Austin Jones on 10/21/2013.  
Please email him at austinmj at bu dot edu with any questions or comments.

The software in this package is an implementation of the algorithm used in the 
manuscript "Temporal Logic Inference for Classification and Prediction from 
Data" written by Zhaodan Kong, Austin Jones, Ana Medina Ayala,  Ebru Aydin Gol, 
and Calin Belta.  This manuscript has been submitted to the 2014 International 
Conference on Hybrid Systems: Computation and Control (HSCC 2014).  Its abstract 
is listed below

**Abstract**
   This paper presents an inference algorithm that can 
discover temporal logic properties of a system from data. Our algorithm
operates on finite time system trajectories that are labeled
according to whether or not they demonstrate some desirable system properties
(e.g. ``the car successfully stops before hitting an obstruction''). A temporal
logic formula that can discriminate between the desirable behaviors and the 
undesirable ones is constructed. The formulae also
indicate possible causes for each set of behaviors (e.g. ``If the speed of the
car is greater than 15 m/s within 0.5s of brake
application, the obstruction will be struck'') which can be used to tune
designs or to perform on-line monitoring to ensure the desired behavior. We
introduce reactive parameter signal temporal logic (rPSTL), a fragment of
parameter signal temporal logic (PSTL) that is
expressive enough
to capture causal, spatial, and temporal relationships in data.  We define a
partial order over the set of rPSTL formulae that is based on language
inclusion. This order enables a directed search over this set, i.e.
given a candidate rPSTL formula that does not adequately match the observed
data, we can automatically construct a formula that will fit the data at least
as well. Two case studies, one involving a cattle herding scenario and one
involving a stochastic
hybrid gene circuit model, are presented to illustrate our approach.

*** End of abstract ***

The details of how to use this software may be found in the help file of the 
function ClassandPred, which produces an rSTL formula for classification and 
prediction given

1) A set of possible variables that can appear in the mined formula
2) Limit on the length of the mined formula
3) A set of system traces
4) Labels for the traces corresponding to whether or not they satisfy some 
desired property
5) Sampling times of the traces
6) Time separation between cause and effect formulae (see manuscript)
7) Bounds of parameters that may be mined
8) Parameters for the simulated annealing subroutine
9) Allowed number of misclassified signals
10) Maximum cost of formula that can be expanded in the next iteration of the 
search

An example of how to use this software is given via the function BN_test.  
This function uses the data from the gene network example used in the 
manuscript.  It returns a formula that describes the repressing effect of the 
protein tetR on the expression of the protein RBF.   Please see the following 
paper for information on how the data was generated.

@INPROCEEDINGS{GolCDC2013,
  author = {Gol, Ebru Aydin and Densmore, Douglas and Belta, Calin},
  title = {Data-driven verification of synthetic gene networks},
  booktitle = {52nd IEEE Conference on Decision and Control (CDC)},
  year = {2013}
}

}