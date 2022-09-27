
function List = ListInitialization(G)
% Initializes the list of formulae to be checked. 
%
% INPUTS - G - Array which represents the formulae to be searched at the 
%             first iteration.  Each row of G is a formula given in
%             numerical form, e.g. the temporal logic operators and
%             inequality signs are given as integers.  The function
%             num2symbols converts it to the standard form.
% OUTPUTS - List - Cell vector of PSTL formulae. Temporally bounded linear 
%                 predicates are given as triples  Tis, where T is a
%                 temporal operator ('F' for eventually, 'G' for always),                
%                 i is a dimension of the signal, and s is  the direction              
%                 of the inequality ('<' or '>').   'F1<vG2>' represents 
%                 the formula  $(F_{[\tau_1,\tau_2)} x_1 < \pi_1)$.
%
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University


    List = cell(size(G,1),1);
    
    for i=1:size(G,1)
        List{i} = G(i,1:end);
        if List{i}(1)==1
            List{i}(1)='G';
        elseif List{i}(1)==2
            List{i}(1)='F';
        end
        if List{i}(3)==1
            List{i}(3)='>';
        elseif List{i}(3)==2
            List{i}(3)='<';
        end            
    end

end