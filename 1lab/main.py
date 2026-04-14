import abc

#1. основа: координаты и ходы
class Move:
    """объект, описывающий перемещение фигуры"""
    def __init__(self, start_pos, end_pos, piece_captured=None, special_effect=None):
        self.start_pos = start_pos  # (row, col)
        self.end_pos = end_pos
        self.piece_captured = piece_captured
        self.special_effect = special_effect #для превращения пешек или взятия на проходе

#2. абстрактный класс фигуры
class Piece(abc.ABC):
    def __init__(self, color):
        self.color = color  # 'W' или 'B'

    @abc.abstractmethod
    def get_valid_moves(self, position, board):
        """каждая фигура сама определяет, куда она может ходить"""
        pass

    def __str__(self):
        return self.char if self.color == 'W' else self.char.lower()

#3. фигуры шахмат
class Pawn(Piece):
    char = 'P'
    def get_valid_moves(self, pos, board):
        moves = []
        r, c = pos
        direction = -1 if self.color == 'W' else 1
        
        #ход вперед
        if 0 <= r + direction < 8 and board.grid[r + direction][c] is None:
            moves.append((r + direction, c))
            #двойной ход
            start_row = 6 if self.color == 'W' else 1
            if r == start_row and board.grid[r + 2*direction][c] is None:
                moves.append((r + 2*direction, c))
        
        #взятия
        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.grid[nr][nc]
                if target and target.color != self.color:
                    moves.append((nr, nc))
                #логика взятия на проходе будет добавлена здесь через board.history
        return moves

class Knight(Piece):
    char = 'N'
    def get_valid_moves(self, pos, board):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            nr, nc = pos[0] + dr, pos[1] + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board.grid[nr][nc] is None or board.grid[nr][nc].color != self.color:
                    moves.append((nr, nc))
        return moves

class King(Piece):
    char = 'K'
    def get_valid_moves(self, pos, board):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = pos[0] + dr, pos[1] + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if board.grid[nr][nc] is None or board.grid[nr][nc].color != self.color:
                        moves.append((nr, nc))
        return moves

#4. фигуры шашек
class Checker(Piece):
    char = 'X'
    def get_valid_moves(self, pos, board):
        moves = []
        r, c = pos
        direction = -1 if self.color == 'W' else 1
        #простые ходы
        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and board.grid[nr][nc] is None:
                moves.append((nr, nc))
            #простая логика взятия
            elif 0 <= r + 2*direction < 8 and 0 <= c + 2*dc < 8:
                mid_p = board.grid[r + direction][c + dc]
                if mid_p and mid_p.color != self.color and board.grid[r + 2*direction][c + 2*dc] is None:
                    moves.append((r + 2*direction, c + 2*dc))
        return moves

#5. шахматная доска и логика игры
class Board:
    def __init__(self, mode='chess'):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.history = []  #для отката ходов
        self.mode = mode
        self.setup_board()

    def setup_board(self):
        if self.mode == 'chess':
            #расстановка пешек
            for i in range(8):
                self.grid[6][i] = Pawn('W')
                self.grid[1][i] = Pawn('B')
            # кони и короли (для примера)
            self.grid[7][1], self.grid[7][6] = Knight('W'), Knight('W')
            self.grid[0][1], self.grid[0][6] = Knight('B'), Knight('B')
            self.grid[7][4], self.grid[0][4] = King('W'), King('B')
        else:
            #расстановка шашек
            for r in range(3):
                for c in range(8):
                    if (r + c) % 2 == 1: self.grid[r][c] = Checker('B')
            for r in range(5, 8):
                for c in range(8):
                    if (r + c) % 2 == 1: self.grid[r][c] = Checker('W')

    def display(self, valid_moves=None):
        print("\n  0 1 2 3 4 5 6 7")
        for r in range(8):
            line = f"{r} "
            for c in range(8):
                if valid_moves and (r, c) in valid_moves:
                    line += "* "  #подсказка хода
                else:
                    piece = self.grid[r][c]
                    line += (str(piece) if piece else ".") + " "
            print(line)

    def move_piece(self, start, end):
        r1, c1 = start
        r2, c2 = end
        piece = self.grid[r1][c1]
        captured = self.grid[r2][c2]
        
        #сохранение в историю
        self.history.append(Move(start, end, captured))
        
        #перемещение
        self.grid[r2][c2] = piece
        self.grid[r1][c1] = None

        #превращение пешки
        if isinstance(piece, Pawn) and (r2 == 0 or r2 == 7):
            self.grid[r2][c2] = King(piece.color) #авто превращение в сильную фигуру

    def undo(self):
        if not self.history:
            print("История пуста!")
            return
        last_move = self.history.pop()
        r1, c1 = last_move.start_pos
        r2, c2 = last_move.end_pos
        
        self.grid[r1][c1] = self.grid[r2][c2]
        self.grid[r2][c2] = last_move.piece_captured
        print(f"Откат хода: {r2,c2} -> {r1,c1}")

#6. осн цикл программы
def main():
    mode = input("Выберите режим (1 - шахматы, 2 - щашки): ")
    game_mode = 'chess' if mode == '1' else 'checkers'
    board = Board(game_mode)
    
    current_color = 'W'

    while True:
        board.display()
        print(f"Ход игрока: {current_color}")
        cmd = input("Введите ход (r1 c1 r2 c2), 'u' для отката или 'q' для выхода: ").split()
        
        if not cmd: continue
        if cmd[0] == 'q': break
        if cmd[0] == 'u':
            board.undo()
            current_color = 'B' if current_color == 'W' else 'W'
            continue

        try:
            r1, c1, r2, c2 = map(int, cmd)
            piece = board.grid[r1][c1]

            if piece and piece.color == current_color:
                valid_moves = piece.get_valid_moves((r1, c1), board)
                
                #показ подсказки (если нужно увидеть ходы)
                if (r2, c2) not in valid_moves:
                    print(f"Недопустимый ход! Возможные: {valid_moves}")
                    continue
                
                board.move_piece((r1, c1), (r2, c2))
                current_color = 'B' if current_color == 'W' else 'W'
            else:
                print("Там нет вашей фигуры!")
        except Exception as e:
            print(f"Ошибка ввода: {e}")

if name == "__main__":
    main()
