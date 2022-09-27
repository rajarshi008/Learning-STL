function phi_c = recoverCause(phi)
% Recovers the cause function phi_c from \neg phi_c.

phi_c = phi;
for j = 1:floor(length(phi)/4)+1
    
    if phi_c((j-1)*4+1) == 'F'
        phi_c((j-1)*4+1) = 'G';
    elseif phi_c((j-1)*4+1) == 'G'
        phi_c((j-1)*4+1) = 'F';
    end
    if phi_c((j-1)*4+3) == '<'
         phi_c((j-1)*4+3) = '>';
    elseif phi_c((j-1)*4+3) == '>'
         phi_c((j-1)*4+3) = '<';
    end
    if j < floor(length(phi)/4)+1
        if phi_c(j*4) == 'v'
            phi_c(j*4) = '^';
        elseif phi_c(j*4) == '^'
            phi_c(j*4) = 'v';
        end
    end
end
end