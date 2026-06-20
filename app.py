import pygame as pg
import sys
import webbrowser
from pathlib import Path
import pygame_gui

from models.representation_model import Graph_Representation
from models.derivative import Derivative
from models.integral import Integral
from models.eq_solver import Equation_Solver
from models.extrema import Extrema
from models.matrix_lab import Matrix_Lab
from models.collatz import CollatzSeries
from models.fibonacci import FibonacciSeries


class App:
    """Single-window shell.
    """

    SIDEBAR_BG = pg.Color("#1E1E2E")
    CONTENT_BG = pg.Color("#181825")
    ACCENT = pg.Color("#2E86AB")

    def __init__(self):
        pg.init()
        info = pg.display.Info()
        self.WIDTH, self.HEIGHT = info.current_w, info.current_h
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), flags=pg.FULLSCREEN)
        pg.display.set_caption("MATHeng")
        self.clock = pg.time.Clock()

        self.sidebar_w = max(280, self.WIDTH // 6)
        self.panel_rect = pg.Rect(self.sidebar_w + 3, 0, self.WIDTH - self.sidebar_w - 3, self.HEIGHT)
        self.panel_surface = pg.Surface((self.panel_rect.width, self.panel_rect.height)).convert()

        base = Path(__file__).resolve().parent
        self.theme = (base / "themes" / "theme_sidebar.json").as_posix()
        self.font_dir = (base / "assets" / "font" / "font.ttf").as_posix()
        self.bfont_dir = (base / "assets" / "font" / "fontb.ttf").as_posix()

        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), theme_path=self.theme)
        self.manager.add_font_paths("JetBrains Mono", self.font_dir)
        try:
            self.manager.add_font_paths("JetBrains Mono Bold", self.bfont_dir)
        except Exception:
            pass

        self.routes = {}
        self.expressions_open = True
        self.series_open = True  # Added toggle state for Series
        self._build_sidebar()


        self._factories = {
            "Graph": lambda: Graph_Representation(
                surface=self.panel_surface,
                WIDTH=self.panel_rect.width,
                HEIGHT=self.panel_rect.height,
                CLOCK=self.clock,
            ),
            "Derivative": lambda: Derivative(surface=self.panel_surface),
            "Integral": lambda: Integral(surface=self.panel_surface),
            "Eq_Solver": lambda: Equation_Solver(surface=self.panel_surface),
            "Extrema": lambda: Extrema(surface=self.panel_surface),
            "Matrix": lambda: Matrix_Lab(surface=self.panel_surface),
            "Collatz": lambda: CollatzSeries(surface=self.panel_surface),
            "Fibonacci": lambda: FibonacciSeries(surface=self.panel_surface),
        }
        self._pages = {}
        self.active_key = None
        self.active_page = None
        self.select("Graph")

    def _build_sidebar(self):
        pad = 24
        x = pad
        w = self.sidebar_w - pad * 2
        btn_h = 52
        gap = 12

        self.title = pygame_gui.elements.UILabel(
            relative_rect=pg.Rect((x, 36), (w, 40)),
            text="MATHeng", manager=self.manager, object_id="#title",
        )
        self.subtitle = pygame_gui.elements.UILabel(
            relative_rect=pg.Rect((x, 76), (w, 24)),
            text="Mathematics Engine", manager=self.manager, object_id="#subtitle",
        )

        y = 140
        self.graph_btn = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((x, y), (w, btn_h)),
            text="  Graph", manager=self.manager, object_id="#nav_item",
        )
        self.routes[self.graph_btn] = "Graph"
        y += btn_h + gap

        # --- Expressions Section ---
        self.expr_header = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((x, y), (w, btn_h)),
            text="  Expressions", manager=self.manager, object_id="#nav_group",
        )
        y += btn_h + gap

        self.expr_items = []
        sub = [
            ("Extrema", "Extrema"),
            ("Derivative", "Derivative"),
            ("Integrator", "Integral"),
            ("Eq. Solver", "Eq_Solver"),
        ]
        ex = x + 18
        ew = w - 18
        eh = 44
        for label, route in sub:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pg.Rect((ex, y), (ew, eh)),
                text="    " + label, manager=self.manager, object_id="#nav_subitem",
            )
            self.routes[btn] = route
            self.expr_items.append(btn)
            y += eh + 8

        y += gap

        # --- Series Section (Added) ---
        self.series_header = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((x, y), (w, btn_h)),
            text="  Series", manager=self.manager, object_id="#nav_group",
        )
        y += btn_h + gap

        self.series_items = []
        series_sub = [
            ("Fibonacci", "Fibonacci"),
            ("Collatz", "Collatz"),
        ]
        for label, route in series_sub:
            btn = pygame_gui.elements.UIButton(
                relative_rect=pg.Rect((ex, y), (ew, eh)),
                text="    " + label, manager=self.manager, object_id="#nav_subitem",
            )
            self.routes[btn] = route
            self.series_items.append(btn)
            y += eh + 8
            
        y += gap

        # --- Matrix & AI Sections ---
        self.matrix_btn = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((x, y), (w, btn_h)),
            text="  Matrix Lab", manager=self.manager, object_id="#nav_item",
        )
        self.routes[self.matrix_btn] = "Matrix"
        y += btn_h + gap

        self.agents_btn = pygame_gui.elements.UIButton(
            relative_rect=pg.Rect((x, y), (w, btn_h)),
            text="  AI Agents", manager=self.manager, object_id="#nav_item",
        )
        self.routes[self.agents_btn] = "Agents"

    def _set_expressions_visibility(self, visible):
        for btn in self.expr_items:
            btn.show() if visible else btn.hide()
            
    def _set_series_visibility(self, visible):
        for btn in self.series_items:
            btn.show() if visible else btn.hide()

    def select(self, key):
        if key == "Agents":
            webbrowser.open("http://localhost:8000")
            return
        if key not in self._factories:
            return
        if key not in self._pages:
            self._pages[key] = self._factories[key]()
        self.active_key = key
        self.active_page = self._pages[key]

    def _translate_event(self, event):
        """Return a copy of mouse events translated into panel-local coords."""
        if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION):
            d = dict(event.__dict__)
            if "pos" in d:
                px, py = d["pos"]
                d["pos"] = (px - self.panel_rect.x, py - self.panel_rect.y)
            return pg.event.Event(event.type, d)
        if event.type == pg.MOUSEWHEEL:
            d = dict(event.__dict__)
            mx, my = pg.mouse.get_pos()
            d["pos"] = (mx - self.panel_rect.x, my - self.panel_rect.y)
            return pg.event.Event(event.type, d)
        return event

    def _point_in_panel(self, event):
        if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION):
            return self.panel_rect.collidepoint(event.pos)
        if event.type == pg.MOUSEWHEEL:
            return self.panel_rect.collidepoint(pg.mouse.get_pos())
        return True

    def run(self):
        self._set_expressions_visibility(self.expressions_open)
        self._set_series_visibility(self.series_open)  # Initialize series visibility
        
        while True:
            dt = self.clock.tick(75) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element in self.routes:
                    self.select(self.routes[event.ui_element])
                    continue
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.expr_header:
                    self.expressions_open = not self.expressions_open
                    self._set_expressions_visibility(self.expressions_open)
                    continue
                    
                if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.series_header:
                    self.series_open = not self.series_open
                    self._set_series_visibility(self.series_open)
                    continue

                self.manager.process_events(event)

                if self.active_page is not None and self._point_in_panel(event):
                    self.active_page.process_event(self._translate_event(event))

            self.manager.update(dt)
            if self.active_page is not None:
                self.active_page.update(dt)

            self.screen.fill(self.CONTENT_BG)
            pg.draw.rect(self.screen, self.SIDEBAR_BG, pg.Rect(0, 0, self.sidebar_w, self.HEIGHT))
            pg.draw.line(self.screen, self.ACCENT, (self.sidebar_w, 0), (self.sidebar_w, self.HEIGHT), 3)

            if self.active_page is not None:
                self.active_page.draw(self.panel_surface)
                self.screen.blit(self.panel_surface, self.panel_rect.topleft)

            self.manager.draw_ui(self.screen)
            pg.display.flip()

if __name__ == "__main__":
    App().run()