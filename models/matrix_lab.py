import pygame
import pygame_gui
import sympy as sp
from pathlib import Path


class MatrixInput:
    def __init__(self, entries=None):
        self.entries = entries or []

    def get_text(self):
        if not self.entries:
            return ""
        lines = []
        for row in self.entries:
            tokens = []
            for entry in row:
                text = entry.get_text().strip()
                if not text:
                    text = "0"
                    entry.set_text("0")
                tokens.append(text)
            lines.append(" ".join(tokens))
        return " ; ".join(lines)


class Matrix_Lab:


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
        field_w = min(420, self.WIDTH // 18)
        f_w = min(420, self.WIDTH//6)
        top = self.HEIGHT // 8

        self.label_a = self._caption("Matrix A", cx - f_w - 20, top - 30)
        self.matrix_a_row = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((cx - field_w - 80, top), (field_w, 40)),
            manager=self.manager,
            placeholder_text="C",
        )
        self.matrix_a_col = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((cx - field_w - 80 - field_w - 20, top), (field_w, 40)),
            manager=self.manager,
            placeholder_text="R",
        )

        self.label_b = self._caption("Matrix B", cx + 20, top - 30)

        self.matrix_b_row = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((cx + 20, top), (field_w, 40)),
            manager=self.manager,
            placeholder_text="R",
        )
        self.matrix_b_col = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((cx + 20 + field_w + 20, top), (field_w, 40)),
            manager=self.manager,
            placeholder_text="C",
        )

        self.input_a = MatrixInput()
        self.input_b = MatrixInput()
        self.matrix_a_entries = []
        self.matrix_b_entries = []
        self.current_a_size = (0, 0)
        self.current_b_size = (0, 0)
        
        self.matrix_start_y = top + 60
        self.center_a = cx - field_w - 90
        self.center_b = cx + field_w + 30

        ops = [
            ("Determinant A", self.op_det),
            ("Inverse A", self.op_inv),
            ("Transpose A", self.op_transpose),
            ("Rank A", self.op_rank),
            ("Eigenvalues A", self.op_eigen),
            ("A x B", self.op_multiply),
            ("A + B", self.op_add),
            ("Swap A & B", self.op_interchange),
        ]
        self.op_buttons = {}
        btn_w = 190
        btn_h = 44
        gap = 14
        cols = 4
        grid_w = cols * btn_w + (cols - 1) * gap
        start_x = cx - grid_w // 2
        start_y = top + self.HEIGHT // 2
        
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
        
    def _update_layout(self):
        a_bottom = self.matrix_start_y
        if self.current_a_size[0] > 0:
            a_bottom = self.matrix_start_y + self.current_a_size[0] * 35
            
        b_bottom = self.matrix_start_y
        if self.current_b_size[0] > 0:
            b_bottom = self.matrix_start_y + self.current_b_size[0] * 35
            
        max_bottom = max(a_bottom, b_bottom, self.matrix_start_y) + 20
        max_bottom = max(max_bottom, self.HEIGHT // 8 + self.HEIGHT // 2)
        
        btn_w = 190
        btn_h = 44
        gap = 14
        cols = 4
        grid_w = cols * btn_w + (cols - 1) * gap
        start_x = self.WIDTH // 2 - grid_w // 2
        start_y = max_bottom
        
        i = 0
        for btn in self.op_buttons:
            row, col = divmod(i, cols)
            bx = start_x + col * (btn_w + gap)
            by = start_y + row * (btn_h + gap)
            btn.set_relative_position((bx, by))
            i += 1
            
        self.result_top = start_y + 2 * (btn_h + gap) + 30

    def _rebuild_matrices(self):
        try:
            a_r = int(self.matrix_a_col.get_text())
        except ValueError:
            a_r = 0
        try:
            a_c = int(self.matrix_a_row.get_text())
        except ValueError:
            a_c = 0
            
        try:
            b_r = int(self.matrix_b_row.get_text())
        except ValueError:
            b_r = 0
        try:
            b_c = int(self.matrix_b_col.get_text())
        except ValueError:
            b_c = 0

        a_r = max(0, min(a_r, 5))
        a_c = max(0, min(a_c, 5))
        b_r = max(0, min(b_r, 5))
        b_c = max(0, min(b_c, 5))

        if (a_r, a_c) != self.current_a_size:
            for row in self.matrix_a_entries:
                for entry in row:
                    entry.kill()
            self.matrix_a_entries = []
            if a_r > 0 and a_c > 0:
                start_x = int(self.center_a - (a_c * 50 - 5) / 2)
                for i in range(a_r):
                    row_entries = []
                    for j in range(a_c):
                        rect = pygame.Rect((start_x + j * 50, self.matrix_start_y + i * 35), (45, 30))
                        entry = pygame_gui.elements.UITextEntryLine(
                            relative_rect=rect,
                            manager=self.manager,
                            placeholder_text="0"
                        )
                        entry.set_text("0")
                        row_entries.append(entry)
                    self.matrix_a_entries.append(row_entries)
            self.current_a_size = (a_r, a_c)
            self.input_a.entries = self.matrix_a_entries
            self._update_layout()

        if (b_r, b_c) != self.current_b_size:
            for row in self.matrix_b_entries:
                for entry in row:
                    entry.kill()
            self.matrix_b_entries = []
            if b_r > 0 and b_c > 0:
                start_x = int(self.center_b - (b_c * 50 - 5) / 2)
                for i in range(b_r):
                    row_entries = []
                    for j in range(b_c):
                        rect = pygame.Rect((start_x + j * 50, self.matrix_start_y + i * 35), (45, 30))
                        entry = pygame_gui.elements.UITextEntryLine(
                            relative_rect=rect,
                            manager=self.manager,
                            placeholder_text="0"
                        )
                        entry.set_text("0")
                        row_entries.append(entry)
                    self.matrix_b_entries.append(row_entries)
            self.current_b_size = (b_r, b_c)
            self.input_b.entries = self.matrix_b_entries
            self._update_layout()

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

    def op_interchange(self):

        a_vals = [[e.get_text() for e in row] for row in self.matrix_a_entries]
        b_vals = [[e.get_text() for e in row] for row in self.matrix_b_entries]

        ar_text = self.matrix_a_col.get_text()
        ac_text = self.matrix_a_row.get_text()
        br_text = self.matrix_b_row.get_text()
        bc_text = self.matrix_b_col.get_text()
        

        self.matrix_a_col.set_text(br_text)
        self.matrix_a_row.set_text(bc_text)
        self.matrix_b_row.set_text(ar_text)
        self.matrix_b_col.set_text(ac_text)

        self.current_a_size = (0, 0)
        self.current_b_size = (0, 0)
        self._rebuild_matrices()
        

        for i, row in enumerate(self.matrix_a_entries):
            for j, entry in enumerate(row):
                if i < len(b_vals) and j < len(b_vals[i]):
                    entry.set_text(b_vals[i][j])
                    

        for i, row in enumerate(self.matrix_b_entries):
            for j, entry in enumerate(row):
                if i < len(a_vals) and j < len(a_vals[i]):
                    entry.set_text(a_vals[i][j])

    def process_event(self, event):
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            handler = self.op_buttons.get(event.ui_element)
            if handler:
                handler()

    def update(self, time_delta):
        self._rebuild_matrices()
        self.manager.update(time_delta)
    
    @property
    def matrix_a_size(self):
        return (int(self.matrix_a_row.get_text()), int(self.matrix_a_col.get_text()))
    
    @property
    def matrix_b_size(self):
        return (int(self.matrix_b_row.get_text()), int(self.matrix_b_col.get_text()))

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