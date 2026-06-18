import pygame
import pygame_gui
from tools.eq_solver import solve
from tools.convert_latex import convert_latex, return_latex_surface
from pathlib import Path


class Equation_Solver:
    def __init__(self, surface):
        self.SURFACE = surface
        self.WIDTH = surface.get_width()
        self.HEIGHT = surface.get_height()
        self.theme = Path(__file__).resolve().parent.parent / "themes" / "theme.json"
        self.font_directory = (Path(__file__).resolve().parent.parent / 'assets' / 'font' / 'font.ttf').as_posix()
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), self.theme)
        self.manager.add_font_paths("JetBrains Mono", self.font_directory)
        self.title_font = pygame.font.Font(self.font_directory, 22)
        self.input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, self.HEIGHT / 10.8), (self.WIDTH // 2, self.HEIGHT / 21.6)),
            manager=self.manager,
            placeholder_text="Enter Equation",
            anchors={'centerx': 'centerx'}
        )
        self.solve_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, self.HEIGHT / 10.8 + self.HEIGHT / 21.6 + 20), (self.WIDTH // 2, self.HEIGHT / 21.6)),
            text="Calculate",
            manager=self.manager,
            anchors={'centerx': 'centerx'}
        )
        self.equation = None
        self.error_message = None
        self.result_surf = None
        self.font = pygame.font.Font(self.font_directory, 15)

    def eq_solve(self):
        self.error_message = None
        equation = self.input_box.get_text().strip()
        if not equation:
            self.error_message = "Error: Please enter an equation."
            return
        try:
            self.equation = solve(equation)
        except Exception as e:
            self.equation = None
            self.error_message = f"Error solving equation: {str(e)}"

    def process_event(self, event):
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.solve_button:
            self.eq_solve()
            if self.equation is not None:
                try:
                    self.result_surf = return_latex_surface(convert_latex(self.equation))
                except Exception as e:
                    self.error_message = str(e)

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, surface):
        surface.fill((30, 30, 46))
        title = self.title_font.render("Equation Solver", True, (205, 214, 244))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, self.HEIGHT // 20))
        self.manager.draw_ui(surface)
        if self.error_message:
            error_surf = self.font.render(self.error_message, True, (200, 50, 50))
            surface.blit(error_surf, (100, 230))
        elif self.equation is not None and self.result_surf is not None:
            surface.blit(self.result_surf, (100, 230))
