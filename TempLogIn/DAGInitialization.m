
function G = DAGInitialization(V)
% Initialization of the graph search algorithm.  This builds the formulae
% of length 1.
%
%INPUTS - V - Vector of the indices of variables that may appear in the mined
%             formula, e.g. V = [1,2] means the first and second dimensions
%             of the trace may appear in the formulae.
%
%OUTPUTS - G - Array which represents the formulae to be searched at the 
%             first iteration.  Each row of G is a formula given in
%             numerical form, e.g. the temporal logic operators and
%             inequality signs are given as integers.  The function
%             num2symbols converts it to the standard form.
%
% Last updated 10/21/13
%
% Author: HyNeSs lab
%         Boston University


    num_basic_nodes = length(V); % number of basic nodes
    O = zeros(2,1); % set of temporal operators, with the first element
    % corresponding to always and the second one to eventually
    greater_equal = zeros(2,1); % intializing relational operators
    G = [];
    c = 0;

    for i=1:num_basic_nodes
        for j=1:size(O,1)
            for k=1:size(greater_equal,1)
                c = c + 1;
                G(c,:) = [j i k];
            end
        end
    end

end
