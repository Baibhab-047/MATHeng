import pygame
import sympy as sp
import pygame_gui
from pathlib import Path
from tools.differentiation import differentiate
from tools.parse_function import parse_function
from tools.convert_latex import return_latex_surface, convert_latex


class Derivative:
    def __init__(self, surface):
        self.WIDTH = surface.get_width()
        self.HEIGHT = surface.get_height()
        self.surface = surface
        self.font_directory = (Path(__file__).resolve().parent.parent / 'assets' / 'font' / 'font.ttf').as_posix()
        self.x = sp.Symbol('x')
        self.theme = Path(__file__).resolve().parent.parent / "themes" / "theme.json"
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), self.theme)
        self.manager.add_font_paths("JetBrains Mono", self.font_directory)

        self.title_font = pygame.font.Font(self.font_directory, 22)
        self.input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, self.HEIGHT / 10.8), (self.WIDTH // 3.6, self.HEIGHT / 21.6)),
            manager=self.manager,
            placeholder_text="Enter function (e.g., x^2)",
            anchors={'centerx': 'centerx'}
        )
        self.order_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((-self.WIDTH // 14.4, self.HEIGHT / 10.8 + self.HEIGHT / 21.6 + 20), (self.WIDTH // 7.2 - 5, self.HEIGHT / 21.6)),
            manager=self.manager,
            placeholder_text="Order (Default: 1)",
            anchors={'centerx': 'centerx'}
        )
        self.calculate_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.WIDTH // 14.4, self.HEIGHT / 10.8 + self.HEIGHT / 21.6 + 20), (self.WIDTH // 7.2 - 5, self.HEIGHT / 21.6)),
            text="Calculate",
            manager=self.manager,
            anchors={'centerx': 'centerx'}
        )
        self.derivative_expression = None
        self.error_message = None
        self.result_surf = None
        self.font = pygame.font.Font(self.font_directory, 15)

    def calculate_derivative(self):
        self.error_message = None
        expression_raw = self.input_box.get_text().strip()
        order_raw = self.order_box.get_text().strip()
        if not expression_raw:
            self.error_message = "Error: Please enter an expression."
            return
        if order_raw == "":
            order = 1
        else:
            try:
                order = int(order_raw)
                if order < 1:
                    raise ValueError
            except ValueError:
                self.error_message = "Error: Order must be a positive integer."
                return
        try:
            parsed_expr = parse_function(expression_raw)
            self.derivative_expression = self.derivative(parsed_expr, order)
        except Exception:
            self.derivative_expression = None
            self.error_message = "Math Error: Invalid expression structure."

    def derivative(self, expression, order=1):
        return differentiate(expression, self.x, order)

    def process_event(self, event):
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.calculate_button:
            self.calculate_derivative()
            if self.derivative_expression is not None:
                self.result_surf = return_latex_surface(convert_latex(self.derivative_expression))

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, surface):
        surface.fill((30, 30, 46))
        title = self.title_font.render("Derivative", True, (205, 214, 244))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, self.HEIGHT // 20))
        self.manager.draw_ui(surface)
        if self.error_message:
            error_surf = self.font.render(self.error_message, True, (200, 50, 50))
            surface.blit(error_surf, (100, 300))
        elif self.derivative_expression is not None and self.result_surf is not None:
            surface.blit(self.result_surf, (100, 300))
