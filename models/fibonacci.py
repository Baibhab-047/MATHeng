import pygame
import pygame_gui
from pathlib import Path
from tools.series import fibonacci

class FibonacciSeries:
    def __init__(self, surface):
        self.surface = surface
        self.WIDTH = surface.get_width()
        self.HEIGHT = surface.get_height()
        self.theme = Path(__file__).resolve().parent.parent / "themes" / "theme.json"
        self.font_directory = (Path(__file__).resolve().parent.parent / 'assets' / 'font' / 'font.ttf').as_posix()
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), self.theme)
        self.manager.add_font_paths("JetBrains Mono", self.font_directory)
        self.title_font = pygame.font.Font(self.font_directory, 22)
        self.input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, self.HEIGHT / 10.8), (self.WIDTH // 3.6, self.HEIGHT / 21.6)),
            manager=self.manager,
            placeholder_text="Enter number (e.g., 10)",
            anchors={'centerx': 'centerx'}
        )
        self.calculate_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, self.HEIGHT / 10.8 + self.HEIGHT / 21.6 + 20), (self.WIDTH // 3.6, self.HEIGHT / 21.6)),
            text="Calculate",
            manager=self.manager,
            anchors={'centerx': 'centerx'}
        )
        self.error_message = None
        self.result_surf = None
        self.font = pygame.font.Font(self.font_directory, 15)
    def update(self, time_delta):
        self.manager.update(time_delta)
    def process_event(self, event):
        self.manager.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.calculate_button:
                    try:
                        n = int(self.input_box.get_text().strip())
                        result = fibonacci(n)
                        self.result_surf = self.font.render(f"Fibonacci({n}) = {result}", True, (205, 214, 244))
                    except ValueError as e:
                        self.error_message = f"Error: {e}"
    def draw(self, surface):
        surface.fill((30, 30, 46))
        title = self.title_font.render("Fibonacci Series", True, (205, 214, 244))
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, self.HEIGHT // 20))
        self.manager.draw_ui(surface)
        if self.error_message:
            error_surf = self.font.render(self.error_message, True, (200, 50, 50))
            surface.blit(error_surf, (100, 260))
        elif self.result_surf is not None:
            surface.blit(self.result_surf, (100, 260))




        