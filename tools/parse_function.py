from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor, implicit_application

def parse_function(function_str):

    transformations = (standard_transformations + (implicit_multiplication, convert_xor, implicit_application))

    try:

        return parse_expr(function_str, transformations=transformations)
    
    except Exception as e:

        print(f"Error parsing function: {e}")

        return str(e)