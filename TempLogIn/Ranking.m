function rnk = Ranking(G,c)
% Ranks the formulae in G based on the cost of their parent formulae.
%
% INPUTS - G - Array which represents the formulae that were searched
%              at the last iteration. Each row of G is a formula given
%              in numerical form, e.g. the temporal logic operators and
%              inequality signs are given as integers.  The function
%              num2symbols converts it to the standard form.
%          c - Vector representing the calculated costs of the formulae in
%              G.
%
% OUTPUTS -  rnk - Vector which gives the ranking of the candidate formulae
%                in List based on the formulae's parents.
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University


    for i=1:size(G,1)
        num_parents = ceil(size(G(i,:),1)/4);
        cost = 0;
        for j=1:num_parents
            cost = cost + c(find(ismember(G,G(i,4*(j-1)+1:4*(j-1)+3)),1),1);
        end
        List_cost = (1/num_parents)*cost;
    end
    % Sort data
    [srt, idxSrt]  = sort(List_cost);
    % Find where are the repetitions
    idxRepeat      = [false diff(srt) == 0];
    % Rank with tieds but w/o skipping
    rnkNoSkip      = cumsum(~idxRepeat);
    % Preallocate rank
    rnk            = 1:numel(List_cost);
    % Adjust for tieds (and skip)
    rnk(idxRepeat) = rnkNoSkip(idxRepeat);
    % Sort back
    rnk(idxSrt)=rnk;

end