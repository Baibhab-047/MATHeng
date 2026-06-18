import sympy as sp
from tools.parse_function import parse_function

def solve(function_str):

    left_str, right_str = function_str.split("=")
    
    left_expr = sp.sympify(parse_function(left_str.strip()))

    right_expr = sp.sympify(parse_function(right_str.strip()))

    Equation = sp.Eq(left_expr, right_expr)

    symbols = Equation.free_symbols - {sp.I, sp.pi, sp.E}

    variable = list(symbols)[0]

    result = sp.solve(Equation, variable)

    if isinstance(result, list):
        
        result.sort(key=lambda x: x.is_real is False)

    return result



    
    