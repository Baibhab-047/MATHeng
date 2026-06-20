import pygame
import pygame_gui
from pathlib import Path

from tools.maxmin import find_extrema
from tools.convert_latex import convert_latex, return_latex_surface


class Extrema:
    def __init__(self, surface):
        self.surface = surface
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.theme = Path(__file__).resolve().parent.parent / "themes" / "theme.json"
        self.font_directory = (Path(__file__).resolve().parent.parent / 'assets' / 'font' / 'font.ttf').as_posix()
        self.manager = pygame_gui.UIManager((self.width, self.height), self.theme)
        self.manager.add_font_paths("JetBrains Mono", self.font_directory)
        self.title_font = pygame.font.Font(self.font_directory, 22)
        self.extrema_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, self.height / 10.8), (self.width // 3.6, self.height / 21.6)),
            manager=self.manager,
            placeholder_text="Expression",
            anchors={'centerx': 'centerx'}
        )
        self.extrema_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, self.height / 10.8 + self.height / 21.6 + 20), (self.width // 3.6, self.height / 21.6)),
            text="Calculate",
            manager=self.manager,
            anchors={'centerx': 'centerx'}
        )
        self.error_message = None
        self.extrema = None
        self.result_surf = None
        self.font = pygame.font.Font(self.font_directory, 15)

    def max_min(self):
        self.error_message = None
        raw_string = self.extrema_input.get_text().strip().replace("e", "E").replace("pi", "PI").replace("π", "PI")
        if not raw_string:
            self.error_message = "Error: Please enter an expression."
            return
        try:
            self.extrema = find_extrema(raw_string)
        except Exception:
            self.extrema = None
            self.error_message = "Error Parsing Expression"

    def process_event(self, event):
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.extrema_button:
            self.max_min()
            if self.extrema is not None:
                self.result_surf = return_latex_surface(convert_latex(self.extrema))

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, surface):
        surface.fill((30, 30, 46))
        title = self.title_font.render("Extrema", True, (205, 214, 244))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, self.height // 20))
        self.manager.draw_ui(surface)
        y = self.height / 10.8 + self.height / 21.6 + 70
        if self.error_message:
            error_surf = self.font.render(self.error_message, True, (200, 50, 50))
            surface.blit(error_surf, (100, y))
        elif self.extrema is not None and self.result_surf is not None:
            surface.blit(self.result_surf, (100, y))
