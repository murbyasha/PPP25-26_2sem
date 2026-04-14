import abc

#1. объекты ходов для истории и отката
class Move:
    """описывает всё, что произошло за ход"""
    def __init__(self, start, end, piece_moved, captured=None, was_promotion=False):
        self.start = start
        self.end = end
        self.piece_moved = piece_moved
        self.captured = captured
        self.was_promotion = was_promotion

#2. баз класс фигуры
class Piece(abc.ABC):
    def __init__(self, color):
        self.color = color  # 'W' или 'B'

    @abc.abstractmethod
    def get_valid_moves(self, pos, board):
        """метод полиморфно реализуется в каждой фигуре"""
        pass

    def _get_sliding_moves(self, pos, board, directions):
        """логика для фигур, ходящих по линиям - ладья, слон, ферзь"""
        moves = []
        r, c = pos
        for dr, dc in directions:
            for i in range(1, 8):
                nr, nc = r + dr * i, c + dc * i
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board.grid[nr][nc]
                    if target is None:
                        moves.append((nr, nc))
                    elif target.color != self.color:
                        moves.append((nr, nc))
                        break #взяли фигуру и остановились
                    else:
                        break #уперлись в свою фигуру
                else:
                    break
        return moves

    def __str__(self):
        return self.char if self.color == 'W' else self.char.lower()

#3. ост шахматные фигуры 
class Pawn(Piece):
    char = 'P'
    def get_valid_moves(self, pos, board):
        moves = []
        r, c = pos
        direction = -1 if self.color == 'W' else 1
        
        #ход вперед
        if 0 <= r + direction < 8 and board.grid[r + direction][c] is None:
            moves.append((r + direction, c))
            #двойной ход в начале
            start_row = 6 if self.color == 'W' else 1
            if r == start_row and board.grid[r + 2 * direction][c] is None:
                moves.append((r + 2 * direction, c))
        
        #взятия
        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.grid[nr][nc]
                if target and target.color != self.color:
                    moves.append((nr, nc))
                
                #взятие на проходе
                if board.history:
                    last_move = board.history[-1]
                    if isinstance(last_move.piece_moved, Pawn) and \
                       abs(last_move.start[0] - last_move.end[0]) == 2 and \
                       last_move.end == (r, nc):
                        moves.append((nr, nc))
        return moves

class Knight(Piece):
    char = 'N'
    def get_valid_moves(self, pos, board):
        moves = []
        offsets = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
        for dr, dc in offsets:
            nr, nc = pos[0]+dr, pos[1]+dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board.grid[nr][nc] is None or board.grid[nr][nc].color != self.color:
                    moves.append((nr, nc))
        return moves

class Bishop(Piece):
    char = 'B'
    def get_valid_moves(self, pos, board):
        return self._get_sliding_moves(pos, board, [(-1,-1), (-1,1), (1,-1), (1,1)])

class Rook(Piece):
    char = 'R'
    def get_valid_moves(self, pos, board):
        return self._get_sliding_moves(pos, board, [(-1,0), (1,0), (0,-1), (0,1)])

class Queen(Piece):
    char = 'Q'
    def get_valid_moves(self, pos, board):
        dirs = [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)]
        return self._get_sliding_moves(pos, board, dirs)

class King(Piece):
    char = 'K'
    def get_valid_moves(self, pos, board):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = pos[0]+dr, pos[1]+dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if board.grid[nr][nc] is None or board.grid[nr][nc].color != self.color:
                        moves.append((nr, nc))
        return moves

#4. шашки (наследование от Piece)
class Checker(Piece):
    char = 'X'
    def get_valid_moves(self, pos, board):
        moves = []
        r, c = pos
        dir = -1 if self.color == 'W' else 1
        #ходы по диагонали
        for dc in [-1, 1]:
            nr, nc = r + dir, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board.grid[nr][nc] is None:
                    moves.append((nr, nc))
                #взятие
                else:
                    tr, tc = nr + dir, nc + dc
                    if 0 <= tr < 8 and 0 <= tc < 8:
                        if board.grid[nr][nc].color != self.color and board.grid[tr][tc] is None:
                            moves.append((tr, tc))
        return moves

#5. класс доски и логики игры
class Board:
    def __init__(self, mode='chess'):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.history = []
        self.mode = mode
        self._setup()

    def _setup(self):
        if self.mode == 'chess':
            order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
            for i, cls in enumerate(order):
                self.grid[0][i] = cls('B'); self.grid[7][i] = cls('W')
                self.grid[1][i] = Pawn('B'); self.grid[6][i] = Pawn('W')
        else:
            for r in range(3):
                for c in range(8):
                    if (r + c) % 2 == 1: self.grid[r][c] = Checker('B')
            for r in range(5, 8):
                for c in range(8):
                    if (r + c) % 2 == 1: self.grid[r][c] = Checker('W')

    def display(self, hints=None):
        print("\n    0 1 2 3 4 5 6 7")
        print("  +-----------------")
        for r in range(8):
            row_str = f"{r} | "
            for c in range(8):
                if hints and (r, c) in hints:
                    row_str += "* " #подсказка хода
                else:
                    p = self.grid[r][c]
                    row_str += (str(p) if p else ".") + " "
            print(row_str)

    def move(self, r1, c1, r2, c2):
        piece = self.grid[r1][c1]
        valid = piece.get_valid_moves((r1, c1), self)
        
        if (r2, c2) not in valid:
            return False

        captured = self.grid[r2][c2]
        was_promotion = False

        #логика взятия на проходе (удаление пешки сбоку)
        if isinstance(piece, Pawn) and c1 != c2 and captured is None:
            captured = self.grid[r1][c2]
            self.grid[r1][c2] = None

        #запись в историю
        self.history.append(Move((r1,c1), (r2,c2), piece, captured))

        #перемещение
        self.grid[r2][c2] = piece
        self.grid[r1][c1] = None

        #превращение пешки (в ферзя)
        if isinstance(piece, Pawn) and (r2 == 0 or r2 == 7):
            self.grid[r2][c2] = Queen(piece.color)
            self.history[-1].was_promotion = True
            
        return True

    def undo(self):
        if not self.history: return False
        m = self.history.pop()
        #если было превращение, возвращаем пешку вместо ферзя
        self.grid[m.start[0]][m.start[1]] = m.piece_moved
        self.grid[m.end[0]][m.end[1]] = None
        
        #возвращаем сбитую фигуру (в т.ч. для взятия на проходе)
        if m.captured:
            c_row = m.end[0] if not (isinstance(m.piece_moved, Pawn) and m.start[1] != m.end[1] and not self.grid[m.end[0]][m.end[1]]) else m.start[0]
            #восстанавливаем на конечную клетку
            self.grid[m.end[0]][m.end[1]] = m.captured
        return True

#6. осн цикл
def play():
    mode_choice = input("Выберите игру: 1 - шахматы, 2 - шашки: ")
    game = Board('chess' if mode_choice == '1' else 'checkers')
    turn = 'W'

    while True:
        game.display()
        print(f"Ход: {'Белые' if turn == 'W' else 'Черные'}")
        inp = input("Команды: 'r1 c1 r2 c2' (ход), 'h r1 c1' (подсказка), 'u' (откат), 'q' (выход): ").lower().split()
        
        if not inp: continue
        if inp[0] == 'q': break
        
        if inp[0] == 'u':
            if game.undo(): turn = 'B' if turn == 'W' else 'W'
            continue
            
        if inp[0] == 'h': #подсказка допустимых ходов
            r, c = int(inp[1]), int(inp[2])
            p = game.grid[r][c]
            if p: game.display(p.get_valid_moves((r, c), game))
            continue

        try:
            r1, c1, r2, c2 = map(int, inp)
            piece = game.grid[r1][c1]
            if piece and piece.color == turn:
                if game.move(r1, c1, r2, c2):
                    turn = 'B' if turn == 'W' else 'W'
                else:
                    print("!!! Недопустимый ход")
            else:
                print("!!! Выберите свою фигуру")
        except:
            print("!!! Ошибка ввода")

if name == "__main__":
    play()
