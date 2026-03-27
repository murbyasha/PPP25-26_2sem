import pygame
import sys
import math

# Инициализация Pygame
pygame.init()

# ----------------------------------------------------------------------
# Параметры окна и доски
# ----------------------------------------------------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# Параметры гексагональной сетки (шестиугольники с плоскими вершинами)
HEX_RADIUS = 40           # радиус описанной окружности
HEX_WIDTH = 2 * HEX_RADIUS
HEX_HEIGHT = math.sqrt(3) * HEX_RADIUS
HEX_HORIZONTAL_SPACING = HEX_WIDTH * 3 / 4
HEX_VERTICAL_SPACING = HEX_HEIGHT

# Цвета
COLOR_BG = (30, 30, 30)
COLOR_CELL = (200, 200, 200)
COLOR_SELECTED = (255, 255, 0, 128)   # жёлтый полупрозрачный
COLOR_MOVE = (0, 255, 0, 128)         # зелёный полупрозрачный
COLOR_CAPTURE = (255, 0, 0, 128)      # красный (для взятия)

# Цвета игроков
PLAYER_COLORS = {
    'red': (200, 50, 50),
    'green': (50, 200, 50),
    'blue': (50, 50, 200)
}
PIECE_COLORS = {
    'red': (255, 100, 100),
    'green': (100, 255, 100),
    'blue': (100, 100, 255)
}

# ----------------------------------------------------------------------
# Гексагональная доска: координаты в кубической системе (q, r, s)
# ----------------------------------------------------------------------
class Hex:
    """Представляет гексагональную клетку в кубических координатах."""
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.s = -q - r

    def __eq__(self, other):
        # Исправлено: проверяем, что other не None
        if other is None:
            return False
        return self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def distance(self, other):
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs(self.s - other.s)) // 2

# Направления для шестиугольника (плоские вершины)
HEX_DIRECTIONS = [
    Hex(1, 0), Hex(1, -1), Hex(0, -1),
    Hex(-1, 0), Hex(-1, 1), Hex(0, 1)
]

# ----------------------------------------------------------------------
# Базовый класс фигуры
# ----------------------------------------------------------------------
class Piece:
    def __init__(self, owner, hex_pos):
        self.owner = owner          # 'red', 'green', 'blue'
        self.hex = hex_pos          # объект Hex
        self.symbol = None          # символ для отображения

    def get_possible_moves(self, board):
        """Возвращает список клеток (Hex), куда может пойти фигура.
           Должен быть переопределён в подклассах."""
        raise NotImplementedError

    def __repr__(self):
        return f"{self.symbol}({self.owner})"

# ----------------------------------------------------------------------
# Конкретные классы фигур (упрощённые для гексагональной доски)
# ----------------------------------------------------------------------
class Pawn(Piece):
    def __init__(self, owner, hex_pos):
        super().__init__(owner, hex_pos)
        self.symbol = '♟'

    def get_possible_moves(self, board):
        moves = []
        # Направление движения зависит от игрока
        forward_map = {
            'red': [Hex(1, -1), Hex(1, 0)],          # два направления вперёд (примерно вниз-вправо)
            'green': [Hex(0, -1), Hex(-1, 0)],       # вниз-влево
            'blue': [Hex(-1, 1), Hex(0, 1)]          # вверх
        }
        
        # Движение вперёд
        for d in forward_map.get(self.owner, []):
            new_hex = Hex(self.hex.q + d.q, self.hex.r + d.r)
            if board.is_inside(new_hex) and board.get_piece_at(new_hex) is None:
                moves.append(new_hex)
        
        # Взятие (пешка может бить по тем же направлениям)
        for d in forward_map.get(self.owner, []):
            new_hex = Hex(self.hex.q + d.q, self.hex.r + d.r)
            target = board.get_piece_at(new_hex)
            if target and target.owner != self.owner:
                moves.append(new_hex)
        return moves

class Rook(Piece):
    def __init__(self, owner, hex_pos):
        super().__init__(owner, hex_pos)
        self.symbol = '♜'

    def get_possible_moves(self, board):
        moves = []
        for direction in HEX_DIRECTIONS:
            for dist in range(1, 10):
                new_hex = Hex(self.hex.q + direction.q * dist, self.hex.r + direction.r * dist)
                if not board.is_inside(new_hex):
                    break
                piece = board.get_piece_at(new_hex)
                if piece is None:
                    moves.append(new_hex)
                else:
                    if piece.owner != self.owner:
                        moves.append(new_hex)
                    break
        return moves

class Knight(Piece):
    def __init__(self, owner, hex_pos):
        super().__init__(owner, hex_pos)
        self.symbol = '♞'

    def get_possible_moves(self, board):
        moves = []
        for d1 in HEX_DIRECTIONS:
            step1 = Hex(self.hex.q + d1.q, self.hex.r + d1.r)
            for d2 in HEX_DIRECTIONS:
                if d2 == d1 or d2 == Hex(-d1.q, -d1.r):
                    continue
                step2 = Hex(step1.q + d2.q, step1.r + d2.r)
                if board.is_inside(step2):
                    piece = board.get_piece_at(step2)
                    if piece is None or piece.owner != self.owner:
                        moves.append(step2)
        return moves

class Bishop(Piece):
    def __init__(self, owner, hex_pos):
        super().__init__(owner, hex_pos)
        self.symbol = '♝'

    def get_possible_moves(self, board):
        diagonal_dirs = [HEX_DIRECTIONS[i] for i in [0, 2, 4]]
        moves = []
        for direction in diagonal_dirs:
            for dist in range(1, 10):
                new_hex = Hex(self.hex.q + direction.q * dist, self.hex.r + direction.r * dist)
                if not board.is_inside(new_hex):
                    break
                piece = board.get_piece_at(new_hex)
                if piece is None:
                    moves.append(new_hex)
                else:
                    if piece.owner != self.owner:
                        moves.append(new_hex)
                    break
        return moves

class Queen(Piece):
    def __init__(self, owner, hex_pos):
        super().__init__(owner, hex_pos)
        self.symbol = '♛'

    def get_possible_moves(self, board):
        moves = Rook.get_possible_moves(self, board) + Bishop.get_possible_moves(self, board)
        return list(set(moves))

class King(Piece):
    def __init__(self, owner, hex_pos):
        super().__init__(owner, hex_pos)
        self.symbol = '♚'

    def get_possible_moves(self, board):
        moves = []
        for direction in HEX_DIRECTIONS:
            new_hex = Hex(self.hex.q + direction.q, self.hex.r + direction.r)
            if board.is_inside(new_hex):
                piece = board.get_piece_at(new_hex)
                if piece is None or piece.owner != self.owner:
                    moves.append(new_hex)
        return moves

# ----------------------------------------------------------------------
# Класс доски (гексагональная)
# ----------------------------------------------------------------------
class HexBoard:
    """Гексагональная доска с тремя игроками."""
    def __init__(self, radius=4):
        self.radius = radius
        self.cells = {}
        self.generate_board()
        self.current_turn = 'red'
        self.king_positions = {}

    def generate_board(self):
        """Создаёт все клетки гексагональной доски."""
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                s = -q - r
                if abs(q) <= self.radius and abs(r) <= self.radius and abs(s) <= self.radius:
                    self.cells[Hex(q, r)] = None

    def is_inside(self, hex):
        return hex in self.cells

    def get_piece_at(self, hex):
        return self.cells.get(hex, None)

    def set_piece_at(self, hex, piece):
        if hex in self.cells:
            self.cells[hex] = piece
            if piece:
                piece.hex = hex

    def move_piece(self, start_hex, end_hex):
        """Перемещает фигуру с start_hex на end_hex, если ход допустим."""
        piece = self.get_piece_at(start_hex)
        if piece is None or piece.owner != self.current_turn:
            return False

        possible_moves = piece.get_possible_moves(self)
        if end_hex not in possible_moves:
            return False

        captured = self.get_piece_at(end_hex)
        self.cells[end_hex] = piece
        self.cells[start_hex] = None
        piece.hex = end_hex

        if isinstance(piece, King):
            self.king_positions[piece.owner] = end_hex

        # Смена хода
        turn_order = ['red', 'green', 'blue']
        idx = turn_order.index(self.current_turn)
        self.current_turn = turn_order[(idx + 1) % 3]

        # Превращение пешки
        if isinstance(piece, Pawn):
            if abs(piece.hex.q) == self.radius or abs(piece.hex.r) == self.radius or abs(piece.hex.s) == self.radius:
                self.cells[end_hex] = Queen(piece.owner, end_hex)

        return True

    def get_all_pieces(self):
        """Возвращает список всех фигур."""
        return [p for p in self.cells.values() if p is not None]

    def setup_start_position(self):
        """Расставляет начальные фигуры для трёх игроков."""
        # Очищаем доску
        for hex in self.cells:
            self.cells[hex] = None

        pieces_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        # Красные фигуры (нижняя сторона)
        red_start = [h for h in self.cells if h.r == -self.radius and abs(h.q) <= self.radius]
        red_rank = sorted(red_start, key=lambda h: h.q)
        for i, hex in enumerate(red_rank):
            if i < len(pieces_order):
                self.set_piece_at(hex, pieces_order[i]('red', hex))
        
        red_pawns = [h for h in self.cells if h.r == -self.radius + 1 and abs(h.q) <= self.radius - 1]
        for hex in red_pawns:
            self.set_piece_at(hex, Pawn('red', hex))

        # Зелёные фигуры (левая сторона)
        green_start = [h for h in self.cells if h.q == -self.radius and abs(h.r) <= self.radius]
        green_rank = sorted(green_start, key=lambda h: h.r)
        for i, hex in enumerate(green_rank):
            if i < len(pieces_order):
                self.set_piece_at(hex, pieces_order[i]('green', hex))
        
        green_pawns = [h for h in self.cells if h.q == -self.radius + 1 and abs(h.r) <= self.radius - 1]
        for hex in green_pawns:
            self.set_piece_at(hex, Pawn('green', hex))

        # Синие фигуры (правая сторона)
        blue_start = [h for h in self.cells if h.q + h.r == self.radius and abs(h.q) <= self.radius]
        blue_rank = sorted(blue_start, key=lambda h: h.q)
        for i, hex in enumerate(blue_rank):
            if i < len(pieces_order):
                self.set_piece_at(hex, pieces_order[i]('blue', hex))
        
        blue_pawns = [h for h in self.cells if h.q + h.r == self.radius - 1 and abs(h.q) <= self.radius - 1]
        for hex in blue_pawns:
            self.set_piece_at(hex, Pawn('blue', hex))

        # Сохраняем позиции королей
        for owner in ['red', 'green', 'blue']:
            for hex, piece in self.cells.items():
                if piece and isinstance(piece, King) and piece.owner == owner:
                    self.king_positions[owner] = hex
                    break

# ----------------------------------------------------------------------
# Графический интерфейс (pygame) для гексагональной доски
# ----------------------------------------------------------------------
class HexUI:
    def __init__(self, board):
        self.board = board
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Гексагональные шахматы на троих")
        self.font = pygame.font.SysFont("segoeuisymbol", 40)
        self.selected_hex = None
        self.valid_moves = []

        # Предварительно вычисляем пиксельные координаты для всех клеток
        self.hex_pixels = {}
        self.compute_hex_positions()

    def compute_hex_positions(self):
        """Вычисляет пиксельные координаты для каждой клетки доски."""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        for hex in self.board.cells:
            x = center_x + HEX_HORIZONTAL_SPACING * (hex.q + hex.r / 2)
            y = center_y + HEX_VERTICAL_SPACING * hex.r
            self.hex_pixels[hex] = (x, y)

    def draw_hexagon(self, hex, color, fill=False, border_width=2):
        """Рисует шестиугольник для заданной клетки."""
        center = self.hex_pixels[hex]
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = center[0] + HEX_RADIUS * math.cos(angle_rad)
            y = center[1] + HEX_RADIUS * math.sin(angle_rad)
            points.append((x, y))
        if fill:
            pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, color, points, border_width)

    def draw_board(self):
        """Рисует доску (клетки и фигуры)."""
        for hex in self.board.cells:
            # Определяем цвет клетки
            color = COLOR_CELL
            
            # Исправлено: явная проверка на None
            if self.selected_hex is not None and self.selected_hex == hex:
                self.draw_hexagon(hex, COLOR_SELECTED, fill=True)
            else:
                self.draw_hexagon(hex, color, fill=True)
            
            # Рисуем фигуру
            piece = self.board.get_piece_at(hex)
            if piece:
                piece_color = PIECE_COLORS[piece.owner]
                text = self.font.render(piece.symbol, True, piece_color)
                text_rect = text.get_rect(center=self.hex_pixels[hex])
                self.screen.blit(text, text_rect)

        # Рисуем подсветку возможных ходов
        for hex in self.valid_moves:
            s = pygame.Surface((HEX_RADIUS*2, HEX_RADIUS*2), pygame.SRCALPHA)
            pygame.draw.circle(s, COLOR_MOVE, (HEX_RADIUS, HEX_RADIUS), HEX_RADIUS//2)
            self.screen.blit(s, (self.hex_pixels[hex][0]-HEX_RADIUS, self.hex_pixels[hex][1]-HEX_RADIUS))

    def get_hex_under_mouse(self):
        """Возвращает клетку, на которую указывает мышь."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        min_dist = HEX_RADIUS + 10
        closest = None
        for hex, (cx, cy) in self.hex_pixels.items():
            dx = cx - mouse_x
            dy = cy - mouse_y
            dist = math.hypot(dx, dy)
            if dist < min_dist:
                min_dist = dist
                closest = hex
        if min_dist <= HEX_RADIUS:
            return closest
        return None

    def handle_click(self):
        """Обрабатывает клик мыши."""
        hex = self.get_hex_under_mouse()
        if hex is None:
            return

        if self.selected_hex is None:
            # Выбираем фигуру, если она принадлежит текущему игроку
            piece = self.board.get_piece_at(hex)
            if piece and piece.owner == self.board.current_turn:
                self.selected_hex = hex
                self.valid_moves = piece.get_possible_moves(self.board)
        else:
            # Пытаемся сделать ход
            if hex in self.valid_moves:
                if self.board.move_piece(self.selected_hex, hex):
                    self.selected_hex = None
                    self.valid_moves = []
                else:
                    self.selected_hex = None
                    self.valid_moves = []
            else:
                self.selected_hex = None
                self.valid_moves = []

    def run(self):
        """Главный цикл игры."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click()

            self.screen.fill(COLOR_BG)
            self.draw_board()
            pygame.display.flip()
            clock.tick(60)

# ----------------------------------------------------------------------
# Запуск игры
# ----------------------------------------------------------------------
if __name__ == "__main__":
    board = HexBoard(radius=4)
    board.setup_start_position()
    ui = HexUI(board)
    ui.run()
