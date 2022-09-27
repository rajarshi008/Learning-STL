function new_G = PrunningAndGrowing(G,basis,J_max,c)
%Function used to expand the graph search to the next level.
%
% INPUTS - G - Array which represents the formulae that were searched
%              at the last iteration. Each row of G is a formula given
%              in numerical form, e.g. the temporal logic operators and
%              inequality signs are given as integers.  The function
%              num2symbols converts it to the standard form.
%          basis - List of formulae of length 1 that were initialized using
%                  DAGInitialization.  These are used to expand the
%                  formulae to be searched in the next iteration
%         J_max - The cutoff cost used to prune the graph.  The children of
%                 formulae with cost greater than J_max will not be
%                 included in the subsequent graph expansion.
%         c - Vector representing the calculated costs of the formulae in
%              G.
%
%
%OUTPUT - new_G - Array which represents the formulae to be searched at the
%                 next iteration.
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University

new_G = [];
l = 0;
for i=1:size(G,1)
    if c(i) < J_max
        l= l + 1;
        new_G(l,:) = G(i,:);
    end
end
m = 1;
for j =1:length(basis)
    for k = 1:size(new_G,1)
        new_G_grow_dis(m,:) = [new_G(k,:),1,basis{j}];
        m = m+1;
    end
end

new_G = new_G_grow_dis;
end