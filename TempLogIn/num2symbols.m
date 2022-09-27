function formula = num2symbols(formula)
% Converts a formula in string form to a formula in numerical form.


num_for = ceil(length(formula)/4);

    for j=1:num_for

        if formula((j-1)*4+1)==1
            formula((j-1)*4+1)='G';
        elseif formula((j-1)*4+1)==2
            formula((j-1)*4+1)='F';
        end
        if formula((j-1)*4+3)==1
            formula((j-1)*4+3)='>';
        elseif formula((j-1)*4+3)==2
            formula((j-1)*4+3)='<';
        end
        if j < num_for
            if formula(j*4)==1
                formula(j*4) = 'v';
            elseif formula(j*4) == 2
                 formula(j*4) = '^';
            end
                
        end
    end
end
