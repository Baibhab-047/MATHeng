import pygame as pg
import numpy as np
import sympy as sp
import pygame_gui
from pathlib import Path

from tools.grapher import Plotter
from tools.parse_function import parse_function


class Func:
    def __init__(self, function: list):
        self.functions_data = []
        for func_str in function:
            if '=' in func_str:
                lhs_str, rhs_str = func_str.split('=', 1)
                exp_str = (
                    f"({parse_function(function_str=lhs_str.strip())}) - "
                    f"({parse_function(function_str=rhs_str.strip())})"
                )
                x, y = sp.symbols('x y')
                func = sp.lambdify((x, y), sp.sympify(exp_str), 'numpy')
                self.functions_data.append({'type': 'implicit', 'func': func})
            else:
                x = sp.symbols('x')
                func = sp.lambdify(x, sp.sympify(parse_function(function_str=func_str)), 'numpy')
                self.functions_data.append({'type': 'explicit', 'func': func})


class Graph_Representation:
    def __init__(self, surface, WIDTH, HEIGHT, CLOCK):
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.SURFACE = surface
        self.graph = Plotter(width=self.WIDTH, height=self.HEIGHT)
        self.surf_rect = pg.Rect(0, 0, self.WIDTH * 3 // 4, self.HEIGHT)
        self.CLOCK = CLOCK
        self.theme = Path(__file__).resolve().parent.parent / "themes" / "theme.json"
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), self.theme)
        self.plot_button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((self.WIDTH * 3 // 4 + 10, self.HEIGHT - 50), (self.WIDTH // 4 - 20, 40)),
            text='Plot',
            manager=self.manager
        )

        self.boxes = [
            pygame_gui.elements.UITextEntryLine(
                relative_rect=pg.Rect((self.WIDTH * 3 // 4 + 10, 50 + i * 40), (self.WIDTH // 4 - 20, 30)),
                manager=self.manager,
                placeholder_text="Enter function"
            )
            for i in range(5)
        ]

        self.surf = pg.Surface((self.surf_rect.width, self.surf_rect.height)).convert()
        self.colors = [
            (220, 20, 60),
            (30, 144, 255),
            (50, 205, 50),
            (255, 140, 0),
            (138, 43, 226),
        ]

        self.fn = Func(['x^2'])
        self.matrix = []
        self.recalculate_matrix()

    def update_functions(self):
        functions = [box.get_text().strip().replace("e", "E").replace("pi", "PI").replace("π", "PI") for box in self.boxes if box.get_text().strip()]
        if not functions:
            return []
        self.fn = Func(functions)
        self.recalculate_matrix()
        return self.matrix

    def recalculate_matrix(self):
        self.matrix = []
        if not hasattr(self, 'fn') or not self.fn.functions_data:
            return
        view_span = self.graph.r_bound - self.graph.l_bound
        x_space = np.linspace(
            self.graph.l_bound - view_span * 2,
            self.graph.r_bound + view_span * 2,
            4000
        )
        for item in self.fn.functions_data:
            if item['type'] == 'explicit':
                pts = self.graph.generate_points(x_space, item['func'])
                self.matrix.append({'type': 'explicit', 'coords': pts})
            else:
                pts = self.graph.generate_implicit_points(item['func'])
                self.matrix.append({'type': 'implicit', 'coords': pts})

    def process_event(self, event):
        self.manager.process_events(event)

        if event.type == pg.MOUSEMOTION:
            if pg.mouse.get_pressed()[0] and self.surf_rect.collidepoint(event.pos):
                self.graph.movement(event=['panning', event.rel])

        elif event.type == pg.MOUSEBUTTONUP:
            self.recalculate_matrix()

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_o:
                self.graph.movement(event=['reset'])
                self.recalculate_matrix()

        elif event.type == pg.MOUSEWHEEL:
            m_x, m_y = getattr(event, 'pos', None) or pg.mouse.get_pos()
            if self.surf_rect.collidepoint(m_x, m_y):
                self.graph.movement(event=['zooming', (m_x, m_y), event.y])
                self.recalculate_matrix()

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.plot_button:
                self.matrix = self.update_functions()
                self.graph.draw = True

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, surface):
        surface.fill((30, 30, 46))
        self.surf.fill((255, 255, 255))
        self.graph.draw_graph(surface=self.surf)

        if self.graph.draw:
            self.graph.lines = []
            self.graph.scatter_points = []

            # Batch-classify all matrix entries then plot by type
            explicit_items = [
                (item['coords'], self.colors[i % len(self.colors)])
                for i, item in enumerate(self.matrix)
                if item['type'] == 'explicit'
            ]
            implicit_items = [
                (item['coords'], self.colors[i % len(self.colors)])
                for i, item in enumerate(self.matrix)
                if item['type'] == 'implicit'
            ]

            for coords, color in explicit_items:
                self.graph.plot(math_cords=coords, color=color)
            for coords, color in implicit_items:
                self.graph.plot_scatter(math_cords=coords, color=color)

        self.graph.draw_points(surface=self.surf)
        surface.blit(self.surf, self.surf_rect.topleft)
        self.manager.draw_ui(surface)