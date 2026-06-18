import pygame
import pygame_gui
import sympy as sp
from pathlib import Path

from tools.integrator import integrate
from tools.parse_function import parse_function
from tools.convert_latex import return_latex_surface, convert_latex


class Integral:
    def __init__(self, surface):
        self.WIDTH = surface.get_width()
        self.HEIGHT = surface.get_height()
        self.theme = Path(__file__).resolve().parent.parent / "themes" / "theme.json"
        self.surface = surface
        self.x = sp.Symbol('x')
        self.font_directory = (Path(__file__).resolve().parent.parent / 'assets' / 'font' / 'font.ttf').as_posix()
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), self.theme)
        self.manager.add_font_paths("JetBrains Mono", self.font_directory)
        self.title_font = pygame.font.Font(self.font_directory, 22)
        self.input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, self.HEIGHT / 10.8), (self.WIDTH // 3.6, self.HEIGHT / 21.6)),
            manager=self.manager,
            placeholder_text="Enter function (e.g., x**2)",
            anchors={'centerx': 'centerx'}
        )
        self.calculate_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, self.HEIGHT / 10.8 + self.HEIGHT / 21.6 + 20), (self.WIDTH // 3.6, self.HEIGHT / 21.6)),
            text="Calculate",
            manager=self.manager,
            anchors={'centerx': 'centerx'}
        )
        self.integral_expression = None
        self.error_message = None
        self.result_surf = None
        self.font = pygame.font.Font(self.font_directory, 15)

    def calculate_integral(self):
        self.error_message = None
        expression_raw = self.input_box.get_text().strip()
        if not expression_raw:
            self.error_message = "Error: Please enter an expression."
            return
        try:
            parsed_expression = parse_function(expression_raw)
            self.integral_expression = integrate(parsed_expression, self.x)
        except Exception:
            self.integral_expression = None
            self.error_message = "Error solving integral"

    def process_event(self, event):
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.calculate_button:
            self.calculate_integral()
            if self.integral_expression is not None:
                self.result_surf = return_latex_surface(convert_latex(self.integral_expression))

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, surface):
        surface.fill((30, 30, 46))
        title = self.title_font.render("Integrator", True, (205, 214, 244))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, self.HEIGHT // 20))
        self.manager.draw_ui(surface)
        if self.error_message:
            error_surf = self.font.render(self.error_message, True, (200, 50, 50))
            surface.blit(error_surf, (100, 260))
        elif self.integral_expression is not None and self.result_surf is not None:
            surface.blit(self.result_surf, (100, 260))
