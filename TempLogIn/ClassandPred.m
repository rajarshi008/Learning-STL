function [phi,val,mn,interp] = ClassandPred(V,L_max,P,s,t,trunc,Plimit,Ns,delta,J_max)
% Produces an rSTL formula from labeled data that can be used to classify
% whether or not a given system trace represents a desired behavior and can
% be used to predict whether a system will produce the desired behavior
% based only on a prefix of a trace.
%
%INPUTS - V - Vector of the indices of variables that may appear in the mined
%             formula, e.g. V = [1,2] means the first and second dimensions
%             of the trace may appear in the formulae.
%         L_max - Maximum length (number of linear predicates) that can
%                 appear in either the cause or effect formulae.
%         P - 3D array which contains the traces against which the formula 
%             is to be evaluated.  The first dimension of the array is 
%             the index of the trace.  The second dimension is the                 
%             index of the multi-dimensional signal.  The third index is                   
%             time.  Thus, P(i,j,k) is the value of the jth dimension of              
%             the ith signal at the kth time point.                  
%         s - Labels of the system. s(i) = 1 if the trace P(i,:,:)                     
%             demonstrates the desired behavior and -1 if it does not.                 
%         t - Vector of sampling times for the data in P such that the                       
%             values of P(:,:,k) are taken at time t(k).
%         trunc - Truncation time of the signal.  The effect formula will
%                 be mined based only on the data at time points after
%                 trunc.
%         Plimit - The limits of the space parameters which may be inferred
%                  by the algorithm. P(i,1)  represents the lower bound on                     
%                  the space parameters of predicates involving the ith                     
%                  dimension of a trace. P(i,2) represents an upper bound on                 
%                  the same quantity.                  
%         Ns - Parameters for the simulated annealing algorithm.  Ns(1) is
%              the number of cycles used and Ns(2) is the number of                   
%              trials per cycle.     
%         delta - Number of misclassified signals the user is willing to
%                 tolerate
%         J_max - The cutoff cost used to prune the graph.  The children of
%                 formulae with cost greater than J_max will not be
%                 included in the subsequent graph expansion.
%                                                            
%OUTPUTS - phi - String which represents the rPSTL formula that is mined. 
%                Temporally bounded linear predicates are given as triples
%                Tis, where T is a temporal operator ('F' for eventually,                
%                'G' for always), i is a dimension of the signal, and s is                
%                the direction of the inequality ('<' or '>').  The triples               
%                are connected by either disjunction ('v') or conjunction              
%                ('^').  For instance,  'F1<vG2>' represents the formula                
%                $(F_{[\tau_1,\tau_2)} x_1 < \pi_1) \vee                 
%                (G_{[\tau_3,\tau_4)} x_2 < \pi_2)$
%          val - Optimal valuation of the formula.  The output is given
%                as a vector.  The 4*k+1st and 4*k+2nd element are the                    
%                upper and lower timebounds of the kth  temporal  operator 
%                in the formula phi.               
%          mn - Number of signals the formula misclassifies                       
%          interp - The mined rSTL formula formatted in LaTeX format where 
%                   the 'eventually' operator is denoted as 'F' and the 
%                   'always' operator is denoted as 'G'
%                                
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University

disp('Initializing classification phase');
[phi_e,val_e,mn_e] = findformula(V,L_max,P,s,t,[trunc,max(t)],Plimit,Ns,[],delta,J_max);
disp(['Classification complete.  Classifying formula is ','$',interpret(phi_e,val_e),'$']);
G = zeros(1,length(phi_e));
G(1,:) = symbols2num(phi_e);
disp ('Initializing prediction phase'); 
[phi,val,mn] =findformula(V,L_max,P,s,t,[min(t),trunc,max(t),ceil(length(phi_e)/4)],Plimit,Ns,G,delta,J_max);

negphi_c = phi(length(phi_e)+2:end) ;
phi_c = recoverCause(negphi_c);
interp = ['$F_{[0,',num2str(max(t)),')}(',interpret(phi_c,val(3*ceil(length(phi_e)/4)+1:end)), '\Rightarrow ', interpret(phi_e,val(1:3*ceil(length(phi_e)/4))),')$'];
disp(['Prediction complete.  Total formula is ',interp])


