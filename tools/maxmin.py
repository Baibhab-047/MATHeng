import sympy as sp
from tools.parse_function import parse_function
    
def find_extrema(function_str):

    function = parse_function(function_str)

    if function is not None:

        x = sp.Symbol('x')

        critical_points = sp.solve(sp.diff(function, x), x)

        extrema = []

        for point in critical_points:

            if point.is_real is False or point.has(sp.I):

                continue
            
            second_derivative = sp.diff(function, x, 2).subs(x, point)

            if second_derivative > 0:

                extrema.append((point, 'minima'))

            elif second_derivative < 0:
           
                extrema.append((point, 'maxima'))
 
            else:
           
                extrema.append((point, 'inflection_point'))

        return extrema

    else:

        return None