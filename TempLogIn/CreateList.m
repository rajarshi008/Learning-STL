function [List,c,mr,par] = CreateList(G, P, t, s, Tlimit, Plimit, Ns)
% Creates a list of formulae that are to be searched during the current
% iteration.  


%INPUTS - G - Array which represents the formulae to be searched at the 
%             current iteration.  Each row of G is a formula given in
%             numerical form, e.g. the temporal logic operators and
%             inequality signs are given as integers.  The function
%             num2symbols converts it to the standard form.
%         P - 3D array which contains the traces against which the formula 
%             is to be evaluated.  The first dimension of the array is 
%             the index of the trace.  The second dimension is the                 
%             index of the multi-dimensional signal.  The third index is                   
%             time.  Thus, P(i,j,k) is the value of the jth dimension of              
%             the ith signal at the kth time point.
%         t - Vector of sampling times for the data in P such that the                       
%             values of P(:,:,k) are taken at time t(k).
%         s - Labels of the system. s(i) = 1 if the trace P(i,:,:)
%             demonstrates the desired behavior and -1 if it does not. 
%         Tlimit - The limits of the time parameters which may be inferred
%                  by the algorithm.  If  this vector has two elements,
%                  they  represent the upper and lower bound. If this vector                                   
%                  has four elements, they represent the upper and lower                 
%                  bounds on time parameters for cause formula, the upper                 
%                  bound on time parameters for the effect formula, and                  
%                  the truncation time.                  
%         Plimit - The limits of the space parameters which may be inferred
%                  by the algorithm. P(i,1)  represents the lower bound on                     
%                  the space parameters of predicates involving the ith                     
%                  dimension of a trace. P(i,2) represents an upper bound on                 
%                  the same quantity.                  
%         Ns - Parameters for the simulated annealing algorithm.  Ns(1) is
%              the number of cycles used and Ns(2) is the number of                   
%              trials per cycle. 
%
%OUTPUTS - List - Cell vector of PSTL formulae. Temporally bounded linear 
%                 predicates are given as triples  Tis, where T is a
%                 temporal operator ('F' for eventually, 'G' for always),                
%                 i is a dimension of the signal, and s is  the direction              
%                 of the inequality ('<' or '>').  The triples are               
%                 connected by either disjunction ('v') or conjunction              
%                 ('^').  For instance,  'F1<vG2>' represents the formula                
%                 $(F_{[\tau_1,\tau_2)} x_1 < \pi_1) \vee                 
%                 (G_{[\tau_3,\tau_4)} x_2 < \pi_2)$.
%          c - Vector representing the calculated costs of the formulae in 
%              List.
%          mr - Vector representing the number of signals each formula in
%               List misclassifies.
%          par - optimal valuations of the formulae in List.
%
%
%Note: All outputs have matching indices, e.g. c(k) is the cost associated
%      with the formula List{k}.
%
% Last updated 10/21/13
%
% Author: HyNeSs lab
%         Boston University
c = zeros(size(G,1),1);
mr =  zeros(size(G,1),1);
List = cell(size(G,1),1);
par = cell(size(G,1),1);
for i=1:size(G,1)
    List{i} = num2symbols(G(i,:));
end
for m=1:size(List,1)
    FO = List{m};
    phi = ListParsing(FO);
    [par{m},c(m),mr(m)] = Simulated_Annealing_BN(P,t,s,Tlimit,Plimit,phi,Ns);
end

end