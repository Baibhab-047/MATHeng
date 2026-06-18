import sympy as sp

def differentiate(function_str, variable, order):

    function = function_str

    if function is not None:

        x = variable

        return sp.diff(function, x, order)

    else:

        return None