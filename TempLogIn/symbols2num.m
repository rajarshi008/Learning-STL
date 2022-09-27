function formula = symbols2num(formula)
%Takes a formula from a string to a numerical array.


num_for = floor(length(formula)/4)+1;

    for j=1:num_for

        if formula((j-1)*4+1)=='G'
            formula((j-1)*4+1)=1;
        elseif formula((j-1)*4+1)=='F'
            formula((j-1)*4+1)=2;
        end
        if formula((j-1)*4+3)=='>'
            formula((j-1)*4+3)=1;
        elseif formula((j-1)*4+3)== '<'
            formula((j-1)*4+3)=2;
        end
        if formula((j-1)*4+2) == '1'
             formula((j-1)*4+2) = 1;
        elseif formula((j-1)*4+2) == '2'
            formula((j-1)*4+2) = 2;
        end
        if j < num_for
            if formula((j-1)*4+4)=='v'
                formula((j-1)*4+4) = 1;
            elseif formula((j-1)*4+4)=='^'
                 formula((j-1)*4+4) = 2;
            end
                
        end
    end
end
