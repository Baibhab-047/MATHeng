import sympy as sp
    
def integrate(function_str, variable):

    function = function_str

    if function is not None:

        x = variable

        return sp.integrate(function, x)

    else:

        return None