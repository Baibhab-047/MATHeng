import pygame
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sympy as sp
import io

def convert_latex(latex_string):
    return sp.latex(sp.sympify(latex_string))

def return_latex_surface(text, size=15, color=(255, 255, 255)):

    mpl_color = tuple(c / 255.0 if isinstance(c, int) and c > 1 else c for c in color)

    fig = plt.figure()

    fig.text(0.5, 0.5, f"${text}$", fontsize=size, ha='center', va='center', color=mpl_color)

    buf = io.BytesIO()

    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.05)

    plt.close(fig)

    buf.seek(0)

    surface = pygame.image.load(buf)
    
    return surface