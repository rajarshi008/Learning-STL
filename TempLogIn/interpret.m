function output = interpret(input,val)
% Function used to format a given rSTL formula into a LaTeX readable
% format.
%
%INPUTS - input - String which represents the rPSTL formula that is mined. 
%                Temporally bounded linear predicates are given as triples
%                Tis, where T is a temporal operator ('F' for eventually,                
%                'G' for always), i is a dimension of the signal, and s is                
%                the direction of the inequality ('<' or '>').  The triples               
%                are connected by either disjunction ('v') or conjunction              
%                ('^').  For instance,  'F1<vG2>' represents the formula                
%                $(F_{[\tau_1,\tau_2)} x_1 < \pi_1) \vee                 
%                (G_{[\tau_3,\tau_4)} x_2 < \pi_2)$
%         val - The valuation of input, given
%                as a vector.  The 4*k+1st and 4*k+2nd element are the                    
%                upper and lower timebounds of the kth  temporal  operator 
%                in the formula phi.  
%
%OUTPUTS - output - The input rSTL formula formatted in LaTeX format where 
%                   the 'eventually' operator is denoted as 'F' and the 
%                   'always' operator is denoted as 'G'.
%
% Last updated  10/21/13
% Author: HyNeSs lab
%         Boston University

output = [''];
for k =0:length(val)/3-1
    
    output = [output, '(',char(input(4*k+1)), '_{[', num2str(val(3*k+1)),',',num2str(val(3*k+2)), ')} x_{',num2str(input(4*k+2)), '}',char(input(4*k+3)), num2str(val(3*k+3)), ') '];
    if k < length(val)/3-1 && length(input) > 4*(k+1)
        output = [output,char2symbol(input(4*(k+1)))];
    end
end
end
function out = char2symbol(ch)
if ch == 'v'
    out= '\vee ';
else
    out= '\wedge ';
end
end