function formula=ListParsing(phi)
% Recursively parses an rPSTL formula.
%
% INPUTS - phi - String which represents an rPSTL formula. 
%                Temporally bounded linear predicates are given as triples
%                Tis, where T is a temporal operator ('F' for eventually,                
%                'G' for always), i is a dimension of the signal, and s is                
%                the direction of the inequality ('<' or '>').  The triples               
%                are connected by either disjunction ('v') or conjunction              
%                ('^').  For instance,  'F1<vG2>' represents the formula                
%                $(F_{[\tau_1,\tau_2)} x_1 < \pi_1) \vee                 
%                (G_{[\tau_3,\tau_4)} x_2 < \pi_2)$ 
%
% OUTPUTS - formula - Version of input formula phi with the correct format
%                     needed for the algorithm.
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University



    formula = '';
    while length(phi)>3
        formula = strcat(formula,char(phi(1,1)),num2str(phi(1,2)),char(phi(1,3)),char(phi(1,4)));
        phi = phi(1,5:end);
    end
    formula = strcat(formula,char(phi(1,1)),num2str(phi(1,2)),char(phi(1,3)));

end