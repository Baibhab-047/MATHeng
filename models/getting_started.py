import pygame as pg
import pygame_gui 
import sys
from pathlib import Path

pg.init()

class Intro:
    def __init__(self, surface: pg.Surface):
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.surface = surface

        self.clock= pg.time.Clock()
        self.theme = (Path(__file__).resolve().parent.parent / "themes" / "theme_entry.json").as_posix()
        
        self.manager = pygame_gui.UIManager((self.width, self.height), self.theme)
        self.font_directory = (Path(__file__).resolve().parent.parent / "assets" / "font" / "os.ttf").as_posix()
        self.manager.add_font_paths("Open Sans", self.font_directory)
        self.get_started_label = pygame_gui.elements.UILabel(
            relative_rect=pg.Rect((0, 200), (500, 100)),
            text="Get Started with MATHeng",
            manager=self.manager,
            anchors={"centerx": "centerx"}
        )
        self.button = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((0, 300), (200, 50)),
            text=">>>",
            manager=self.manager,
            anchors={"centerx": "centerx"}
        )

        self.running = True
    
    def run(self):
        while self.running:
            self.surface.fill((255, 255, 255))
            time_delta = self.clock.tick(60) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.button:
                        return "menu"
                self.manager.process_events(event)
            self.manager.update(time_delta)
            self.manager.draw_ui(self.surface)
            pg.display.flip()
        pg.quit()
        sys.exit()

    