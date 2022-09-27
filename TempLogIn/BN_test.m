function BN_test(L_max,V)

% Function used to infer the formula that describes the inverter
% characteristic of the gene network.  The data for this problem is located
% in the file good_behavior1.mat.
%
%INPUTS - L_max - Maximum length (number of linear predicates) that can
%                 appear in either the cause or effect formulae.
%         V - Vector of the indices of variables that may appear in the mined
%             formula, e.g. V = [1,2] means the first and second dimensions
%             of the trace may appear in the formulae.
%
%   Last updated 10/21/13
%   Author: HyNeSs lab
%           Boston University

load('good_behavior1','Nl','N','P1_gh','P2_gh','P1_gl','P2_gl')

Nc = 120; % number of cycles
Nt = 240; % number of trials




% Signals.  P(:,1,:) represents the concentration of the repressor protein 
% tetR and P(:,2,:) represents the concentration of the affected protein
% RFP. Pi_gh represents the protein concentrations for the high output case
% and Pi_gl represents the protein concentrations for the low output cases.
P(:,1,:) = [P1_gh; P1_gl];
P(:,2,:) = [P2_gh; P2_gl];
%Labels of the signals.  The first set of signals in P are dis-satisfying (high output) and
%the second set of signals are satisfying (low output)
s = [-ones(size(P1_gh,1),1);ones(size(P1_gl,1),1)];
Plimit = [min(min([P1_gh,P1_gl])) max(max([P1_gh,P1_gl]));
min(min([P2_gh,P2_gl])) max(max([P2_gh,P2_gl]))];

delta = 10;
    
J_max = 120;
tic
 [phi,val,mn,interp] = ClassandPred(V,L_max,P,s,[1:99],50,Plimit,[Nc,Nt],delta,J_max)
 toc