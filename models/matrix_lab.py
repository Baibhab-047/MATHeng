import pygame
import pygame_gui
import sympy as sp
from pathlib import Path


class Matrix_Lab:
    """Matrix Lab: enter matrices and run linear-algebra operations.
    """

    BG = (24, 24, 37)
    TEXT = (205, 214, 244)
    ERR = (243, 139, 168)
    OK = (166, 227, 161)

    def __init__(self, surface):
        self.surface = surface
        self.WIDTH = surface.get_width()
        self.HEIGHT = surface.get_height()

        self.theme = Path(__file__).resolve().parent.parent / "themes" / "theme.json"
        self.font_directory = (Path(__file__).resolve().parent.parent / "assets" / "font" / "font.ttf").as_posix()

        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), self.theme)
        self.manager.add_font_paths("JetBrains Mono", self.font_directory)

        self.font = pygame.font.Font(self.font_directory, 16)
        self.title_font = pygame.font.Font(self.font_directory, 22)

        cx = self.WIDTH // 2
        field_w = min(420, self.WIDTH // 3)
        top = self.HEIGHT // 8

        self.label_a = self._caption("Matrix A", cx - field_w - 20, top - 30)
        self.input_a = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((cx - field_w - 20, top), (field_w, 40)),
            manager=self.manager,
            placeholder_text="1 2; 3 4",
        )

        self.label_b = self._caption("Matrix B", cx + 20, top - 30)
        self.input_b = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((cx + 20, top), (field_w, 40)),
            manager=self.manager,
            placeholder_text="5 6; 7 8 (for A x B)",
        )

        ops = [
            ("Determinant A", self.op_det),
            ("Inverse A", self.op_inv),
            ("Transpose A", self.op_transpose),
            ("Rank A", self.op_rank),
            ("Eigenvalues A", self.op_eigen),
            ("A x B", self.op_multiply),
            ("A + B", self.op_add),
        ]
        self.op_buttons = {}
        btn_w = 190
        btn_h = 44
        gap = 14
        cols = 4
        grid_w = cols * btn_w + (cols - 1) * gap
        start_x = cx - grid_w // 2
        start_y = top + 80
        for i, (label, handler) in enumerate(ops):
            row, col = divmod(i, cols)
            bx = start_x + col * (btn_w + gap)
            by = start_y + row * (btn_h + gap)
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((bx, by), (btn_w, btn_h)),
                text=label,
                manager=self.manager,
            )
            self.op_buttons[btn] = handler

        self.result_top = start_y + 2 * (btn_h + gap) + 30
        self.error_message = None
        self.result_lines = []

    def _caption(self, text, x, y):
        return pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((x, y), (200, 26)),
            text=text,
            manager=self.manager,
        )

    def parse_matrix(self, raw):
        raw = raw.strip()
        if not raw:
            raise ValueError("empty matrix")
        rows = [r for r in raw.split(";") if r.strip()]
        data = []
        for r in rows:
            tokens = r.replace(",", " ").split()
            data.append([sp.Rational(sp.sympify(t)) for t in tokens])
        widths = {len(r) for r in data}
        if len(widths) != 1:
            raise ValueError("rows have unequal length")
        return sp.Matrix(data)

    def _matrix_to_lines(self, m):
        return [str(m.row(i).tolist()[0]) for i in range(m.rows)]

    def _set_result(self, title, value):
        self.error_message = None
        if isinstance(value, sp.MatrixBase):
            self.result_lines = [title] + self._matrix_to_lines(value)
        elif isinstance(value, (list, tuple)):
            self.result_lines = [title] + [str(v) for v in value]
        else:
            self.result_lines = [title, str(value)]

    def _safe(self, fn):
        try:
            fn()
        except Exception as e:
            self.result_lines = []
            self.error_message = f"Error: {e}"

    def op_det(self):
        self._safe(lambda: self._set_result("det(A) =", self.parse_matrix(self.input_a.get_text()).det()))

    def op_inv(self):
        self._safe(lambda: self._set_result("A^-1 =", self.parse_matrix(self.input_a.get_text()).inv()))

    def op_transpose(self):
        self._safe(lambda: self._set_result("A^T =", self.parse_matrix(self.input_a.get_text()).T))

    def op_rank(self):
        self._safe(lambda: self._set_result("rank(A) =", self.parse_matrix(self.input_a.get_text()).rank()))

    def op_eigen(self):
        def run():
            m = self.parse_matrix(self.input_a.get_text())
            eig = m.eigenvals()
            vals = [f"{k}  (x{v})" for k, v in eig.items()]
            self._set_result("eigenvalues(A) =", vals)
        self._safe(run)

    def op_multiply(self):
        def run():
            a = self.parse_matrix(self.input_a.get_text())
            b = self.parse_matrix(self.input_b.get_text())
            self._set_result("A x B =", a * b)
        self._safe(run)

    def op_add(self):
        def run():
            a = self.parse_matrix(self.input_a.get_text())
            b = self.parse_matrix(self.input_b.get_text())
            self._set_result("A + B =", a + b)
        self._safe(run)

    def process_event(self, event):
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            handler = self.op_buttons.get(event.ui_element)
            if handler:
                handler()

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, surface):
        surface.fill(self.BG)
        self.manager.draw_ui(surface)
        title = self.title_font.render("Matrix Lab", True, self.TEXT)
        surface.blit(title, (surface.get_width() // 2 - title.get_width() // 2, self.HEIGHT // 20))
        if self.error_message:
            s = self.font.render(self.error_message, True, self.ERR)
            surface.blit(s, (surface.get_width() // 2 - s.get_width() // 2, self.result_top))
        else:
            y = self.result_top
            for i, line in enumerate(self.result_lines):
                color = self.OK if i == 0 else self.TEXT
                s = self.font.render(line, True, color)
                surface.blit(s, (surface.get_width() // 2 - s.get_width() // 2, y))
                y += 30
