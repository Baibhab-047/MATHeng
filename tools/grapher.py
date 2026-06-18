import numpy as np
import pygame as pg


class Plotter:
    def __init__(self, width: int, height: int, scale=30):
        self.WIDTH = width
        self.HEIGHT = height
        self.ORIGIN_X = width // 2
        self.ORIGIN_Y = height // 2
        self.SCALE = scale
        self.draw = True
        self.lines = []
        self.scatter_points = []
        self.MAX_SCALE = 500
        self.MIN_SCALE = 5
        pg.font.init()
        self.font = pg.font.SysFont('segoeui', 12)
        self._grid_cache = None
        self._grid_key = None

    @property
    def r_bound(self):
        return (self.WIDTH - self.ORIGIN_X + 500) / self.SCALE

    @property
    def l_bound(self):
        return -(self.ORIGIN_X + 500) / self.SCALE

    @property
    def u_bound(self):
        return (self.ORIGIN_Y + 500) / self.SCALE

    @property
    def d_bound(self):
        return (self.ORIGIN_Y - self.HEIGHT - 500) / self.SCALE

    def _render_grid(self):
        grid = pg.Surface((self.WIDTH, self.HEIGHT)).convert()
        grid.fill((255, 255, 255))
        grid_step = 10 if self.SCALE < 25 else 1
        pixel_step = self.SCALE * grid_step
        offset_x = self.ORIGIN_X % pixel_step
        offset_y = self.ORIGIN_Y % pixel_step
        y_positions = np.arange(offset_y, self.HEIGHT, pixel_step)
        x_positions = np.arange(offset_x, self.WIDTH, pixel_step)

        math_x_values = (x_positions - self.ORIGIN_X) / self.SCALE
        for px, math_x in zip(x_positions, math_x_values):
            pg.draw.line(grid, (235, 235, 235), (px, 0), (px, self.HEIGHT), 1)
            if abs(math_x) > 0.01:
                text = self.font.render(f"{math_x:g}", True, (60, 60, 60))
                grid.blit(text, (px, self.HEIGHT - 25))

        math_y_values = (self.ORIGIN_Y - y_positions) / self.SCALE
        for py, math_y in zip(y_positions, math_y_values):
            pg.draw.line(grid, (235, 235, 235), (0, py), (self.WIDTH, py), 1)
            if abs(math_y) > 0.01:
                text = self.font.render(f"{math_y:g}", True, (60, 60, 60))
                grid.blit(text, (5, py))

        pg.draw.line(grid, (0, 0, 0), (0, self.ORIGIN_Y), (self.WIDTH, self.ORIGIN_Y), 1)
        pg.draw.line(grid, (0, 0, 0), (self.ORIGIN_X, 0), (self.ORIGIN_X, self.HEIGHT), 1)
        return grid

    def draw_graph(self, surface):
        key = (round(self.ORIGIN_X), round(self.ORIGIN_Y), self.SCALE)
        if self._grid_cache is None or key != self._grid_key:
            self._grid_cache = self._render_grid()
            self._grid_key = key
        surface.blit(self._grid_cache, (0, 0))

    def plot(self, math_cords: np.ndarray, color=(255, 0, 0)):
        math_x, math_y = math_cords.T
        view_mask = (
            (math_x > self.l_bound) & (math_x < self.r_bound) &
            (math_y < self.u_bound) & (math_y > self.d_bound) &
            np.isfinite(math_x) & np.isfinite(math_y)
        )
        v_x = math_x[view_mask]
        v_y = math_y[view_mask]
        screen_x = self.ORIGIN_X + v_x * self.SCALE
        screen_y = self.ORIGIN_Y - v_y * self.SCALE
        finite_mask = np.isfinite(screen_y)
        pts = np.column_stack((screen_x[finite_mask], screen_y[finite_mask]))
        self.lines.append((pts, color))
        self.draw = False

    def draw_points(self, surface):
        for pts, color in self.lines:
            if pts.shape[0] >= 2:
                pg.draw.aalines(surface, color, False, pts)


        if self.scatter_points:
            from collections import defaultdict
            grouped: dict[tuple, list[np.ndarray]] = defaultdict(list)
            for pts, color in self.scatter_points:
                grouped[color].append(pts)

            for color, arrays in grouped.items():
                all_pts = np.concatenate(arrays, axis=0)
                w, h = surface.get_size()
                mask = (
                    (all_pts[:, 0] >= 0) & (all_pts[:, 0] < w - 1) &
                    (all_pts[:, 1] >= 0) & (all_pts[:, 1] < h - 1)
                )
                valid = all_pts[mask]
                for point in valid:
                    surface.fill(color, ((point[0], point[1]), (2, 2)))

    def movement(self, event):
        if event[0] == 'panning':
            self.ORIGIN_X += event[1][0]
            self.ORIGIN_Y += event[1][1]
            self.draw = True

        elif event[0] == 'zooming':
            mouse_x, mouse_y = event[1][0], event[1][1]
            math_x = (mouse_x - self.ORIGIN_X) / self.SCALE
            math_y = (self.ORIGIN_Y - mouse_y) / self.SCALE

            if event[2] > 0:
                self.SCALE += 5
            elif event[2] < 0:
                self.SCALE -= 5

            self.SCALE = max(self.MIN_SCALE, min(self.SCALE, self.MAX_SCALE))
            self.ORIGIN_X = mouse_x - math_x * self.SCALE
            self.ORIGIN_Y = mouse_y + math_y * self.SCALE
            self.draw = True

        elif event[0] == 'reset':
            self.ORIGIN_X = self.WIDTH // 2
            self.ORIGIN_Y = self.HEIGHT // 2
            self.SCALE = 50
            self.draw = True

    def generate_points(self, math_x_range: np.ndarray, numpy_function):
        self.num_function = numpy_function
        try:
            math_y = self.num_function(math_x_range)
            if isinstance(math_y, (int, float)):
                math_y = np.full_like(math_x_range, math_y)
            return np.column_stack((math_x_range, math_y))
        except Exception:
            return np.column_stack((math_x_range, np.zeros_like(math_x_range)))

    def generate_implicit_points(self, num_function, resolution=2):
        start_math_x, end_math_x = self.l_bound, self.r_bound
        start_math_y, end_math_y = self.d_bound, self.u_bound

        pixel_width = (end_math_x - start_math_x) * self.SCALE
        pixel_height = (end_math_y - start_math_y) * self.SCALE

        cols = max(2, int(pixel_width / resolution))
        rows = max(2, int(pixel_height / resolution))

        math_x = np.linspace(start_math_x, end_math_x, cols)
        math_y = np.linspace(start_math_y, end_math_y, rows)

        X, Y = np.meshgrid(math_x, math_y)

        try:
            Z = num_function(X, Y)
            if isinstance(Z, (int, float)):
                Z = np.full_like(X, Z)
        except Exception:
            return np.empty((0, 2))


        edges = (
            ((Z * np.roll(Z, shift=-1, axis=1)) <= 0) |
            ((Z * np.roll(Z, shift=-1, axis=0)) <= 0)
        )
        edges[:, -1] = False
        edges[-1, :] = False

        y_idx, x_idx = np.where(edges)
        return np.column_stack((math_x[x_idx], math_y[y_idx]))

    def plot_scatter(self, math_cords: np.ndarray, color=(255, 0, 0)):
        if len(math_cords) == 0:
            return

        math_x, math_y = math_cords.T

        view_mask = (
            (math_x > self.l_bound) & (math_x < self.r_bound) &
            (math_y < self.u_bound) & (math_y > self.d_bound) &
            np.isfinite(math_x) & np.isfinite(math_y)
        )
        v_x = math_x[view_mask]
        v_y = math_y[view_mask]

        screen_x = self.ORIGIN_X + v_x * self.SCALE
        screen_y = self.ORIGIN_Y - v_y * self.SCALE

        pts = np.column_stack((screen_x, screen_y)).astype(np.int32)
        self.scatter_points.append((pts, color))
        self.draw = False