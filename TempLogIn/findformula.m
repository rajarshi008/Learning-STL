
function [phi,par,mn] = findformula(V,L_max,P,s,t,Tlimit,Plimit,Ns,G,delta,J_max)
% The "workhorse" for our classification and prediction algorithms.  This
% is the implementation of Algorithm 1 in the HSCC 2014 paper.  The names
% of the functions used here match the ones described there.
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
%         delta - Number of misclassified signals the user is willing to
%                 tolerate
%         J_max - The cutoff cost used to prune this .  The children of
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
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University

c = [];
for i=1:L_max
    if i==1
        Gtemp =DAGInitialization(V);
        basis = cell(size(Gtemp,1),1);
        for j = 1:size(Gtemp,1)
            basis{j} = Gtemp(j,:);
        end
        
        if length(G) < 1
            G_new =  Gtemp;
            List = ListInitialization(G_new);
            rnk = randi(size(G_new,1),1,size(G_new,1));
        else
            G_new = G;
            G_new = PrunningAndGrowing(G_new,basis, J_max,zeros(size(G_new,1),1));
            [List,c,mr,pars] = CreateList(G_new, P, t, s, Tlimit, Plimit, Ns);
            rnk = Ranking(G_new,c);
        end
        
    else
        
        G_new = PrunningAndGrowing(G_new,basis,J_max,c);
        [List,c,mr,pars] = CreateList(G_new, P, t, s, Tlimit, Plimit, Ns);
        rnk = Ranking(G_new,c);
    end
    if length(c) < 1
        c = zeros(size(G_new,1),1);
        mr = zeros(size(G_new,1),1);
        pars = cell(size(G_new,1),1);
        for m=1:size(c,1)
            phi = ListParsing(num2symbols(G_new(m,:)));
            [pars{m},c(m),mr(m)] = Simulated_Annealing_BN(P,t,s,Tlimit,Plimit,phi,Ns);
        end
    end
    totalList = List;
    while ~isempty(List)
        [phi_1,rnk,mn,par] = PopOutFirstElement(rnk,totalList,mr,pars);
        phi = ListParsing(phi_1);
        if mn <= delta
            return
        end
        
        [G, List] = Maintenance(phi_1,List,G_new);
    end
end