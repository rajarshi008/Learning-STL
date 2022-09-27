function [G, new_List] = Maintenance(formula, List, G_old)
%Removes candidate formula from the graph and list.
%
% INPUTS - formula  - String which represents an rPSTL formula. 
%                Temporally bounded linear predicates are given as triples
%                Tis, where T is a temporal operator ('F' for eventually,                
%                'G' for always), i is a dimension of the signal, and s is                
%                the direction of the inequality ('<' or '>').  The triples               
%                are connected by either disjunction ('v') or conjunction              
%                ('^').  For instance,  'F1<vG2>' represents the formula                
%                $(F_{[\tau_1,\tau_2)} x_1 < \pi_1) \vee                 
%                (G_{[\tau_3,\tau_4)} x_2 < \pi_2)$ 
%         List - Cell array which list the formulae
%         G_old - Array which represents the formulae to be searched at the 
%             first iteration.  Each row of G is a formula given in
%             numerical form, e.g. the temporal logic operators and
%             inequality signs are given as integers.  The function
%             num2symbols converts it to the standard form.
%
%OUTPUTS - G - G_old with formula removed
%          new_List - List with formula removed
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University

    for k = 1:length(List)
        if (length(List{k}) == length(formula)) && min(List{k} == formula)
            break
        end
    end
    

    G = G_old(setdiff(1:size(G_old,1),k),:);
    new_List = List;
    new_List(k) = [];

end