function [phi,rnk,mn,par] = PopOutFirstElement(rnk,List,mr,pars)
%Returns the formula with lowest rank according the ranking algorithm.
%
% INPUTS - rnk - Vector which gives the ranking of the candidate formulae
%                in List based on the formulae's parents.
%           List - Cell vector of PSTL formulae. Temporally bounded linear 
%                 predicates are given as triples  Tis, where T is a
%                 temporal operator ('F' for eventually, 'G' for always),                
%                 i is a dimension of the signal, and s is  the direction              
%                 of the inequality ('<' or '>').  The triples are               
%                 connected by either disjunction ('v') or conjunction              
%                 ('^').  For instance,  'F1<vG2>' represents the formula                
%                 $(F_{[\tau_1,\tau_2)} x_1 < \pi_1) \vee                 
%                 (G_{[\tau_3,\tau_4)} x_2 < \pi_2)$.
%          mr - Vector representing the number of signals each formula in
%               List misclassifies.
%          pars - optimal valuations of the formulae in List.
%
% OUTPUTS - phi - Formula with the lowest rank.
%           rnk - Updated rank vector
%           mn - Number of signals phi misclassifies
%           par - Optimal valuation of phi.
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University

    [value, index] = min(rnk);
    rnk(index) = max(rnk)+1;
    phi = List{index};
    mn = mr(index);
    par = pars{index};

end