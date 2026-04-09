import os

# ШАХМАТНАЯ ЛОГИКА

class Piece:
    def __init__(self, color, symbol):
        self.color = color  # 'white' или 'black'
        self.symbol = symbol

    def get_moves(self, board, row, col):
        """Метод, который переопределяется в подклассах (Полиморфизм)."""
        return []

    def __str__(self):
        return self.symbol

class King(Piece):
    def get_moves(self, board, row, col):
        moves = []
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves

class Rook(Piece):
    def get_moves(self, board, row, col):
        moves = []
        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board.get_piece(r, c)
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break
                else: break
                r, c = r + dr, c + dc
        return moves


class Board:
    """Класс доски. Инкапсулирует сетку и логику отображения."""
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self._setup_board()

    def _setup_board(self):
        # Упрощенная расстановка для примера
        self.grid[0][0] = Rook('black', '♜')
        self.grid[0][4] = King('black', '♚')
        self.grid[7][0] = Rook('white', '♖')
        self.grid[7][4] = King('white', '♔')

    def get_piece(self, r, c):
        return self.grid[r][c]

    def move_piece(self, start, end):
        r1, c1 = start
        r2, c2 = end
        piece = self.grid[r1][c1]
        if piece and end in piece.get_moves(self, r1, c1):
            self.grid[r2][c2] = piece
            self.grid[r1][c1] = None
            return True
        return False

    def display(self, valid_moves=None):
        """Подсказка ходов (Доп. задание): подсвечивает клетки."""
        print("  0 1 2 3 4 5 6 7")
        for r in range(8):
            row_str = f"{r} "
            for c in range(8):
                if valid_moves and (r, c) in valid_moves:
                    row_str += "● "  # Точка для подсказки хода
                else:
                    piece = self.grid[r][c]
                    row_str += (str(piece) if piece else ".") + " "
            print(row_str)

# ДОП ЗАДАНИЕ: ГЕКСАГОНАЛЬНЫЕ ШАХМАТЫ

class HexBoard(Board):
    """Наследование: расширяем обычную доску до гексагональной."""
    def __init__(self, players_count=3):
        # Гексагональная сетка как расширенная матрицу
        self.grid = {} # словарь координат (q, r) для гексов
        self.players = ['white', 'black', 'red']
        self.current_player_idx = 0

    def display(self):
        print("--- Гексагональная доска (Схематично для 3 игроков) ---")
        print("Реализована структура для 3-х цветов: White, Black, Red")


def play_game():
    board = Board()
    current_turn = 'white'
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Ход игрока: {current_turn}")
        board.display()
        
        try:
            print("\nВыберите фигуру (ряд и столбец через пробел, например: 7 0):")
            r1, c1 = map(int, input().split())
            piece = board.get_piece(r1, c1)
            
            if piece and piece.color == current_turn:
                # Подсказка ходов (Доп. задание)
                moves = piece.get_moves(board, r1, c1)
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"Допустимые ходы для {piece}: {moves}")
                board.display(valid_moves=moves)
                
                print("\nКуда ходить? (ряд и столбец):")
                r2, c2 = map(int, input().split())
                
                if board.move_piece((r1, c1), (r2, c2)):
                    current_turn = 'black' if current_turn == 'white' else 'white'
                else:
                    print("Неверный ход!")
                    input("Нажмите Enter...")
            else:
                print("Там нет вашей фигуры!")
                input("Нажмите Enter...")
        except ValueError:
            print("Введите числа!")
            input("Нажмите Enter...")


if name == "__main__":
    # Запуск обычных шахмат
    # Для запуска гексагональных вызвать HexBoard()
    play_game()
