function [par,obj,mn] = Simulated_Annealing_BN(P,t,s,Tlimit,Plimit,FO,Ns)

%
%Finds the optimal valuation of an rPSTL formula by using simulated
%annealing.
%
% File: Simulated_Annealing_BN.m
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
%                               and -1 if it does not.
%                           Tlimit - The limits of the time parameters which
%                                    may be inferred by the algorithm.  If
%                                    this vector has two elements, they
%                                    represent the upper and lower bound.
%                                    If this vector has four elements, they
%                                    represent the upper and lower bounds
%                                    on time parameters for cause formula,
%                                    the upper bound on time parameters for
%                                    the effect formula, and the truncation
%                                    time.
%                           Plimit - The limits of the space parameters
%                                    which may be inferred by the algorithm.  
%                                    P(i,1)  represents the lower bound on 
%                                    the space parameters of predicates
%                                    involving the ith  dimension of a trace.
%                                    P(i,2) represents an upper bound on
%                                    the same quantity.
%                            
%                           FO - rPSTL formula whose valuation is sought.
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
%                           
%                   OUTPUTS: obj - The cost of the mined formula.
%                            mn - Number of signals which are misclassified
%                                 by the mined formula.
%                            par - Optimal valuation of the formula.  The
%                                  output is given as a vector.  The 
%                                  4*k+1st and 4*k+2nd element are the
%                                  upper and lower timebounds of the kth 
%                                  temporal  operator in the formula FO.
%
% Last modified: 10/21/2013
%
% Author:   HyNeSs Lab
%           Boston University
%

%% Parameters

%
na = 0.0; % number of accepted solutions
p1 = 0.7; % probability of accepting worse solution at the start
p50 = 0.001; % probability of accepting worse solution at the end
t1 = -1.0/log(p1); % initial temprature
t50 = -1.0/log(p50); % final temprature
frac = (t50/t1)^(1.0/(Ns(1)-1.0)); % fractional reduction every cycle

% sizes
Nn = size(P,1);
Nv = 1 + (length(FO)-3)/4;
Nm = size(P,3);

% time
if length(Tlimit) == 2
    tmin = Tlimit(1);
    tmax = Tlimit(2);
elseif length(Tlimit) == 4
    tmin = Tlimit(1);
    tmid = Tlimit(2);
    tmax = Tlimit(3);
    trunc = Tlimit(4);
end

% variable
x = P;
xmin = Plimit(:,1);
xmax = Plimit(:,2);


% the interval should be at least Tl long
Tl = 2;

%% Main Function

% initialization
for m =0:Nv-1
    if length(Tlimit)> 2
        if m < trunc
            xi(3*m+1) = tmid;
            xi(3*m+2) = tmax;
            xi(3*m+3) = (xmax(str2num(FO(4*m+2)))+xmin(str2num(FO(4*m+2))))/2;
            
        else
            xi(3*m+1) = tmin;
            xi(3*m+2) = tmid;
            xi(3*m+3) = (xmax(str2num(FO(4*m+2)))+xmin(str2num(FO(4*m+2))))/2;
        end
    else
        xi(3*m+1) = tmin;
        xi(3*m+2) = tmax;
        xi(3*m+3) = (xmax(str2num(FO(4*m+2)))+xmin(str2num(FO(4*m+2))))/2;
    end
end
na = na+1.0;

% current best results so far
xc = xi;
[fc,fmn] = RobustPerformanceSe_BN(x,t,s,xi,FO);

% current temprature
T = t1;

% DeltaE average
DeltaE_avg = 0.0;

%
for i = 1:Ns(1)
    disp(['Cycle: ',num2str(i),' with Temperature: ',num2str(T)])
    % couting number
    nj = 0;
    for j = 1:Ns(2)
        % generate new trial points
        for m =0:Nv-1
            
            if length(Tlimit)> 2
                if m < trunc
                    xi(3*m+1) = xc(3*m+1)+(rand()-0.5)*(tmax-tmid);
                    xi(3*m+2) = xc(3*m+2)+(rand()-0.5)*(tmax-tmid);
                    xi(3*m+3) = xc(3*m+3)+(rand()-0.5)*(xmax(str2num(FO(4*m+2)))-xmin(str2num(FO(4*m+2))))/2;
                    % clip to upper and lower bounds
                    xi(3*m+1) = max(min(xi(3*m+1),tmax-Tl),tmid);
                    xi(3*m+2) = max(min(xi(3*m+2),tmax),xi(3*m+1)+Tl);
                    xi(3*m+3) = max(min(xi(3*m+3),xmax(str2num(FO(4*m+2)))),xmin(str2num(FO(4*m+2))));
                    
                else
                    xi(3*m+1) = xc(3*m+1)+(rand()-0.5)*(tmid-tmin);
                    xi(3*m+2) = xc(3*m+2)+(rand()-0.5)*(tmid-tmin);
                    xi(3*m+3) = xc(3*m+3)+(rand()-0.5)*(xmax(str2num(FO(4*m+2)))-xmin(str2num(FO(4*m+2))))/2;
                    % clip to upper and lower bounds
                    xi(3*m+1) = max(min(xi(3*m+1),tmid-Tl),tmin);
                    xi(3*m+2) = max(min(xi(3*m+2),tmid),xi(3*m+1)+Tl);
                    xi(3*m+3) = max(min(xi(3*m+3),xmax(str2num(FO(4*m+2)))),xmin(str2num(FO(4*m+2))));
                end
            else
                xi(3*m+1) = xc(3*m+1)+(rand()-0.5)*(tmax-tmin);
                xi(3*m+2) = xc(3*m+2)+(rand()-0.5)*(tmax-tmin);
                xi(3*m+3) = xc(3*m+3)+(rand()-0.5)*(xmax(str2num(FO(4*m+2)))-xmin(str2num(FO(4*m+2))))/2;
                % clip to upper and lower bounds
                xi(3*m+1) = max(min(xi(3*m+1),tmax-Tl),tmin);
                xi(3*m+2) = max(min(xi(3*m+2),tmax),xi(3*m+1)+Tl);
                xi(3*m+3) = max(min(xi(3*m+3),xmax(str2num(FO(4*m+2)))),xmin(str2num(FO(4*m+2))));
            end
        end
        % compute robustness degree
        [fs,fsmn] = RobustPerformanceSe_BN(x,t,s,xi,FO);
        %
        if isnan(fs)
            accept = false;
        else
            %
            nj = nj+1;
            %
            DeltaE = abs(fs-fc);
            if fs > fc
                % initialize DeltaE_avg if a worse solution was found on
                % the first iteration
                if (i==1)&(nj==1)
                    DeltaE_avg = DeltaE;
                end
                % objective funciton is worse, generate probability of
                % acceptance
                p = exp(-DeltaE/(DeltaE_avg*T));
                % determine whether to accpet worse point
                if rand()<p % accept the worse solution
                    accept = true;
                else % don't accept the worse solution
                    accept = false;
                end
            else
                % objective function is lower, automatically accept
                accept = true;
            end
        end
        % update currently accepted solution
        if accept == true
            xc = xi;
            fc = fs;
            fmn = fsmn;
            % increment number of accepted solutions
            na = na+1.0;
            % update DeltaE_avg
            DeltaE_avg = (DeltaE_avg*(na-1.0)+DeltaE)/na;
        end
    end
    % lower the temprature for next cycle
    T = frac*T;
end

%% Outputs

%
par = xc;
obj = fc;
mn = fmn;
