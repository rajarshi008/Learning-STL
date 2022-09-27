function [obj,mn] = RobustPerformanceSe_BN(P,t,s,c,formula)

%
%Computes the cost of a given rSTL formula with respect to a set of system
%traces.
%
%
% File: RobustPerformanceSe_BN.m
%
% Description: -1-: INPUTS: P -  3D array which contains the traces against
%                                which the formula is to be evaluated.  The 
%                                first dimension of the array is the index 
%                                of the trace.  The second dimension is the
%                                index of the multi-dimensional signal.
%                                The third index is time.  Thus, P(i,j,k)
%                                is the value of the jth dimension of the
%                                ith signal at the kth time point.
%                           t - Vector of sampling times for the data in P
%                               such that the values of P(:,:,k) are taken
%                               at time t(k).
%                           s - Labels of the system. s(i) = 1 if the trace
%                               P(i,:,:) demonstrates the desired behavior
%                           c - Valuation of the formula.  The output is 
%                               given as a vector.  The 4*k+1st and
%                               4*k+2nd element are the upper and lower 
%                               timebounds of the kth temporal  operator in
%                               the formula. 
%                            
%                           formula - rPSTL formula whose valuation is sought.
%                                The formulae are given as strings where
%                                temporally bounded linear predicates are
%                                given as triples Ti, where T is a
%                                temporal operator ('F' for eventually, 'G'
%                                for always), i is a dimension of the
%                                signal, and s is the direction of the
%                                inequality ('<' or '>').  The triples are
%                                connected by either disjunction ('v') or
%                                conjunction ('^').  For instance,
%                                'F1<vG2>' represents the formula
%                                $(F_{[\tau_1,\tau_2)} x_1 < \pi_1) \vee
%                                (G_{[\tau_3,\tau_4)} x_2 < \pi_2)$,
%                   OUTPUTS: obj - The cost of the formula.
%                            mn - Number of signals which are misclassified
%                                 by the formula.
%                           
%
% Last modified: 10/21/2013
%
% Author:   HyNeSs Lab
%           Boston University


%
Nn = size(P,1);
Nm = size(P,3);

% misclassification number
mn = 0;

% time parameter and scale parameter

%
obj = 0;

numberOfClauses= (length(formula)-3)/4 + 1;
for i = 1:Nn
    % indices
    
    for k = numberOfClauses-1:-1:0
        tp1 = c(3*k+1);
        tp2 = c(3*k+2);
        vp = c(3*k+3);
        i1 = min(find(t>=tp1));
        i2 = max(find(t<=tp2));
        if k < numberOfClauses-1
            FO = formula(4*k+1:4*k+4);
        else
            FO = formula(4*k+1:4*k+3);
        end
        % ============
        % Computation of robustness degree
        % ============
        % robustness degree (first clause)
        if FO(1) == 'F' % eventually
            if FO(3) =='>'
                for j = 1:max(1,Nm-(i2+1))
                    re(j) = max(P(i,str2num(FO(2)),j+i1-1:j+i2-1)-vp);
                end
                rd_tmp = min(re);
            else
                for j = 1:max(1,Nm-(i2+1))
                    re(j) = max(-P(i,str2num(FO(2)),j+i1-1:j+i2-1)+vp);
                end
                rd_tmp = min(re);
            end
        else % always
            if FO(3) == '>'
                for j = 1:max(1,Nm-(i2+1))
                    re(j) = min(P(i,str2num(FO(2)),j+i1-1:j+i2-1)-vp);
                    
                end
                rd_tmp = min(re);
            else
                for j = 1:max(1,Nm-(i2+1))
                    re(j) = min(-P(i,str2num(FO(2)),j+i1-1:j+i2-1)+vp);
                end
                rd_tmp = min(re);
            end
        end
        %
        
        if length(FO) == 4
            if FO(4) == '^'
                rd_positive = min(rd_positive,rd_tmp);
            else
                rd_positive = max(rd_positive,rd_tmp);
            end
        else
            rd_positive = rd_tmp;
        end
    end
    rd_negative = -rd_positive;
    % ==========
    % Evaluation (hingle loss, please consult any machine learning book)
    % ==========
    if s(i) > 0
        obj = obj+max(1-rd_positive,0);
        if rd_positive <=0
            mn = mn+1;
        end
    else
        obj = obj+max(1-rd_negative,0);
        if rd_negative <=0
            mn = mn+1;
        end
    end
    clear re
end
