import sys
from abc import ABC, abstractmethod
from typing import Set, Tuple, Dict, Optional

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def clear():
    print("\n" * 30)

# ==================== КЛАССИЧЕСКИЕ ШАХМАТЫ ====================
def coord(pos: str) -> Tuple[int, int]:
    return ord(pos[0]) - ord('a'), 8 - int(pos[1])
def pos(c: int, r: int) -> str:
    return f"{chr(c + ord('a'))}{8 - r}"

class Piece(ABC):
    def __init__(self, color: str, pos: str):
        self.color = color
        self.pos = pos
    @abstractmethod
    def moves(self, board: 'Board') -> Set[str]: pass

class Pawn(Piece):
    def moves(self, board):
        m = set()
        c, r = coord(self.pos)
        d = -1 if self.color == 'w' else 1
        # вперёд
        if 0 <= r+d < 8 and board.get(pos(c, r+d)) is None:
            m.add(pos(c, r+d))
        # взятие
        for dc in (-1,1):
            if 0 <= c+dc < 8 and 0 <= r+d < 8:
                p = board.get(pos(c+dc, r+d))
                if p and p.color != self.color:
                    m.add(pos(c+dc, r+d))
        return m

class Rook(Piece):
    def moves(self, board):
        m = set()
        c, r = coord(self.pos)
        for dc, dr in ((0,1),(0,-1),(1,0),(-1,0)):
            nc, nr = c+dc, r+dr
            while 0 <= nc < 8 and 0 <= nr < 8:
                p = board.get(pos(nc, nr))
                if p is None:
                    m.add(pos(nc, nr))
                else:
                    if p.color != self.color: m.add(pos(nc, nr))
                    break
                nc += dc; nr += dr
        return m

class Knight(Piece):
    def moves(self, board):
        m = set()
        c, r = coord(self.pos)
        for dc, dr in ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)):
            nc, nr = c+dc, r+dr
            if 0 <= nc < 8 and 0 <= nr < 8:
                p = board.get(pos(nc, nr))
                if p is None or p.color != self.color: m.add(pos(nc, nr))
        return m

class Bishop(Piece):
    def moves(self, board):
        m = set()
        c, r = coord(self.pos)
        for dc, dr in ((1,1),(1,-1),(-1,1),(-1,-1)):
            nc, nr = c+dc, r+dr
            while 0 <= nc < 8 and 0 <= nr < 8:
                p = board.get(pos(nc, nr))
                if p is None:
                    m.add(pos(nc, nr))
                else:
                    if p.color != self.color: m.add(pos(nc, nr))
                    break
                nc += dc; nr += dr
        return m

class Queen(Piece):
    def moves(self, board):
        m = set()
        c, r = coord(self.pos)
        for dc, dr in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)):
            nc, nr = c+dc, r+dr
            while 0 <= nc < 8 and 0 <= nr < 8:
                p = board.get(pos(nc, nr))
                if p is None:
                    m.add(pos(nc, nr))
                else:
                    if p.color != self.color: m.add(pos(nc, nr))
                    break
                nc += dc; nr += dr
        return m

class King(Piece):
    def moves(self, board):
        m = set()
        c, r = coord(self.pos)
        for dc in (-1,0,1):
            for dr in (-1,0,1):
                if dc==dr==0: continue
                nc, nr = c+dc, r+dr
                if 0 <= nc < 8 and 0 <= nr < 8:
                    p = board.get(pos(nc, nr))
                    if p is None or p.color != self.color:
                        m.add(pos(nc, nr))
        return m

class Board:
    def __init__(self):
        self.pieces = {}
        self._setup()
    def _setup(self):
        for c in range(8):
            self.pieces[pos(c,6)] = Pawn('w', pos(c,6))
            self.pieces[pos(c,1)] = Pawn('b', pos(c,1))
        back = ['a','b','c','d','e','f','g','h']
        types = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, t in enumerate(types):
            self.pieces[back[i]+'1'] = t('w', back[i]+'1')
            self.pieces[back[i]+'8'] = t('b', back[i]+'8')
    def get(self, pos): return self.pieces.get(pos)
    def move(self, f, t):
        p = self.get(f)
        if not p or t not in p.moves(self): return False
        captured = self.get(t)
        del self.pieces[f]; self.pieces[t] = p; p.pos = t
        if self.is_check(p.color):  # откат
            del self.pieces[t]; self.pieces[f] = p; p.pos = f
            if captured: self.pieces[t] = captured
            return False
        # превращение пешки
        if isinstance(p, Pawn) and (coord(t)[1] == 0 or coord(t)[1] == 7):
            self.pieces[t] = Queen(p.color, t)
        return True
    def is_check(self, color):
        king = next((p for p in self.pieces.values() if isinstance(p, King) and p.color == color), None)
        if not king: return False
        return self._attacked(king.pos, color)
    def _attacked(self, sq, color):
        for p in self.pieces.values():
            if p.color != color and sq in p.moves(self):
                return True
        return False
    def is_checkmate(self, color):
        if not self.is_check(color): return False
        for pos, p in list(self.pieces.items()):
            if p.color == color:
                for move in p.moves(self):
                    if self._try_move(pos, move): return False
        return True
    def _try_move(self, f, t):
        p = self.get(f)
        if not p or t not in p.moves(self): return False
        captured = self.get(t)
        del self.pieces[f]; self.pieces[t] = p; p.pos = t
        in_check = self.is_check(p.color)
        del self.pieces[t]; self.pieces[f] = p; p.pos = f
        if captured: self.pieces[t] = captured
        return not in_check
    def display(self, highlights=None):
        print("  a b c d e f g h")
        for r in range(8):
            print(8-r, end=" ")
            for c in range(8):
                p = self.get(pos(c,r))
                s = (p.symbol[0] if p else '.')
                if highlights and pos(c,r) in highlights:
                    s = f"\033[42m{s}\033[0m"
                print(s, end=" ")
            print(8-r)
        print("  a b c d e f g h")

# ==================== ГЕКСАГОНАЛЬНЫЕ ШАХМАТЫ ====================
WHITE, BLACK, RED = 0,1,2
COLOR_NAMES = ['Белые','Чёрные','Красные']
DIRS = [(1,-1,0),(1,0,-1),(0,1,-1),(-1,1,0),(-1,0,1),(0,-1,1)]

def add(q,r,s, dq,dr,ds): return q+dq, r+dr, s+ds

class HexPiece(ABC):
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos
    @abstractmethod
    def moves(self, board): pass

class HexPawn(HexPiece):
    def moves(self, board):
        m = set()
        q,r,s = self.pos
        forward = {WHITE:(1,-1,0), BLACK:(-1,1,0), RED:(0,-1,1)}[self.color]
        nq,nr,ns = add(q,r,s, *forward)
        if board.valid(nq,nr,ns) and board.get(nq,nr,ns) is None:
            m.add((nq,nr,ns))
        for d in DIRS:
            if d == forward or d == tuple(-x for x in forward): continue
            nq,nr,ns = add(q,r,s, *d)
            if board.valid(nq,nr,ns):
                p = board.get(nq,nr,ns)
                if p and p.color != self.color:
                    m.add((nq,nr,ns))
        return m

class HexRook(HexPiece):
    def moves(self, board):
        m = set()
        q,r,s = self.pos
        for d in DIRS:
            dq,dr,ds = d
            step = 1
            while True:
                nq,nr,ns = add(q,r,s, dq*step, dr*step, ds*step)
                if not board.valid(nq,nr,ns): break
                p = board.get(nq,nr,ns)
                if p is None:
                    m.add((nq,nr,ns))
                else:
                    if p.color != self.color: m.add((nq,nr,ns))
                    break
                step += 1
        return m

class HexKnight(HexPiece):
    def moves(self, board):
        m = set()
        q,r,s = self.pos
        for d1 in DIRS:
            for d2 in DIRS:
                if d1 == d2 or d1 == tuple(-x for x in d2): continue
                nq = q + d1[0]*2 + d2[0]
                nr = r + d1[1]*2 + d2[1]
                ns = s + d1[2]*2 + d2[2]
                if board.valid(nq,nr,ns):
                    p = board.get(nq,nr,ns)
                    if p is None or p.color != self.color:
                        m.add((nq,nr,ns))
        return m

class HexBishop(HexPiece):
    def moves(self, board):
        m = set()
        q,r,s = self.pos
        diag = [(1,-1,0),(1,0,-1),(0,1,-1),(-1,1,0),(-1,0,1),(0,-1,1)]
        for d in diag:
            dq,dr,ds = d
            step = 1
            while True:
                nq,nr,ns = add(q,r,s, dq*step, dr*step, ds*step)
                if not board.valid(nq,nr,ns): break
                p = board.get(nq,nr,ns)
                if p is None:
                    m.add((nq,nr,ns))
                else:
                    if p.color != self.color: m.add((nq,nr,ns))
                    break
                step += 1
        return m

class HexQueen(HexPiece):
    def moves(self, board):
        m = set()
        q,r,s = self.pos
        for d in DIRS:
            dq,dr,ds = d
            step = 1
            while True:
                nq,nr,ns = add(q,r,s, dq*step, dr*step, ds*step)
                if not board.valid(nq,nr,ns): break
                p = board.get(nq,nr,ns)
                if p is None:
                    m.add((nq,nr,ns))
                else:
                    if p.color != self.color: m.add((nq,nr,ns))
                    break
                step += 1
        return m

class HexKing(HexPiece):
    def moves(self, board):
        m = set()
        q,r,s = self.pos
        for d in DIRS:
            nq,nr,ns = add(q,r,s, *d)
            if board.valid(nq,nr,ns):
                p = board.get(nq,nr,ns)
                if p is None or p.color != self.color:
                    m.add((nq,nr,ns))
        return m

class HexBoard:
    def __init__(self, radius=5):
        self.radius = radius
        self.pieces = {}
        self._setup()
    def valid(self, q,r,s): return q+r+s==0 and max(abs(q),abs(r),abs(s)) <= self.radius
    def get(self, q,r,s): return self.pieces.get((q,r,s))
    def _setup(self):
        # Белые (q=radius)
        self.pieces[(5,-5,0)] = HexKing(WHITE, (5,-5,0))
        self.pieces[(5,-4,-1)] = HexQueen(WHITE, (5,-4,-1))
        self.pieces[(5,-3,-2)] = HexRook(WHITE, (5,-3,-2))
        self.pieces[(5,-2,-3)] = HexKnight(WHITE, (5,-2,-3))
        self.pieces[(5,-1,-4)] = HexBishop(WHITE, (5,-1,-4))
        for i in range(-5,0): self.pieces[(4,i,-4-i)] = HexPawn(WHITE, (4,i,-4-i))
        # Чёрные (r=radius)
        self.pieces[(-5,5,0)] = HexKing(BLACK, (-5,5,0))
        self.pieces[(-4,5,-1)] = HexQueen(BLACK, (-4,5,-1))
        self.pieces[(-3,5,-2)] = HexRook(BLACK, (-3,5,-2))
        self.pieces[(-2,5,-3)] = HexKnight(BLACK, (-2,5,-3))
        self.pieces[(-1,5,-4)] = HexBishop(BLACK, (-1,5,-4))
        for i in range(-5,0): self.pieces[(i,4,-4-i)] = HexPawn(BLACK, (i,4,-4-i))
        # Красные (s=radius)
        self.pieces[(0,-5,5)] = HexKing(RED, (0,-5,5))
        self.pieces[(-1,-4,5)] = HexQueen(RED, (-1,-4,5))
        self.pieces[(-2,-3,5)] = HexRook(RED, (-2,-3,5))
        self.pieces[(-3,-2,5)] = HexKnight(RED, (-3,-2,5))
        self.pieces[(-4,-1,5)] = HexBishop(RED, (-4,-1,5))
        for i in range(-5,0): self.pieces[(i,-4,4-i)] = HexPawn(RED, (i,-4,4-i))
    def move(self, f, t):
        p = self.get(*f)
        if not p or t not in p.moves(self): return False
        captured = self.get(*t)
        del self.pieces[f]; self.pieces[t] = p; p.pos = t
        if self.is_check(p.color):
            del self.pieces[t]; self.pieces[f] = p; p.pos = f
            if captured: self.pieces[t] = captured
            return False
        if isinstance(p, HexPawn) and max(abs(t[0]),abs(t[1]),abs(t[2])) == self.radius:
            self.pieces[t] = HexQueen(p.color, t)
        return True
    def is_check(self, color):
        king = next((p for p in self.pieces.values() if isinstance(p, HexKing) and p.color == color), None)
        if not king: return False
        return self._attacked(king.pos, color)
    def _attacked(self, sq, color):
        for p in self.pieces.values():
            if p.color != color and sq in p.moves(self):
                return True
        return False
    def is_checkmate(self, color):
        if not self.is_check(color): return False
        for pos, p in list(self.pieces.items()):
            if p.color == color:
                for move in p.moves(self):
                    if self._try_move(pos, move): return False
        return True
    def _try_move(self, f, t):
        p = self.get(*f)
        if not p or t not in p.moves(self): return False
        captured = self.get(*t)
        del self.pieces[f]; self.pieces[t] = p; p.pos = t
        in_check = self.is_check(p.color)
        del self.pieces[t]; self.pieces[f] = p; p.pos = f
        if captured: self.pieces[t] = captured
        return not in_check
    def display(self, highlights=None):
        print("Гексагональная доска (координаты q,r,s):")
        for pos, p in self.pieces.items():
            sym = (p.__class__.__name__[3] if hasattr(p,'__class__') else '?')
            if highlights and pos in highlights:
                sym = f"\033[42m{sym}\033[0m"
            print(f"{pos}: {sym} ({COLOR_NAMES[p.color]})")
        print("-"*40)

# ==================== ОСНОВНАЯ ИГРА ====================
def run_chess():
    board = Board()
    turn = 'w'
    while True:
        board.display()
        print(f"Ход {'белых' if turn=='w' else 'чёрных'}")
        cmd = input("Введите ход (e2 e4) или позицию для подсказки (e2): ").strip().split()
        if len(cmd) == 1:
            p = board.get(cmd[0])
            if p and p.color == turn:
                board.display(highlights=p.moves(board))
            else:
                print("Нет вашей фигуры")
            continue
        if len(cmd) == 2 and board.move(cmd[0], cmd[1]):
            if board.is_checkmate(turn):
                board.display()
                print(f"Мат! Победили {'чёрные' if turn=='w' else 'белые'}")
                break
            if board.is_check(turn):
                print("Шах!")
            turn = 'b' if turn == 'w' else 'w'
        else:
            print("Неверный ход")

def run_hex():
    board = HexBoard(radius=5)
    turn = WHITE
    order = [WHITE, BLACK, RED]
    while True:
        board.display()
        print(f"Ход {COLOR_NAMES[turn]}")
        cmd = input("Введите ход (q r s tq tr ts) или координаты фигуры для подсказки: ").strip().split()
        if len(cmd) == 3:
            try:
                q,r,s = map(int, cmd)
                p = board.get(q,r,s)
                if p and p.color == turn:
                    board.display(highlights=p.moves(board))
                else:
                    print("Нет вашей фигуры")
            except:
                print("Неверный формат")
            continue
        if len(cmd) == 6:
            try:
                f = tuple(map(int, cmd[:3]))
                t = tuple(map(int, cmd[3:]))
                if board.move(f, t):
                    nxt = order[(order.index(turn)+1)%3]
                    if board.is_checkmate(nxt):
                        board.display()
                        print(f"Мат! Победили {COLOR_NAMES[turn]}")
                        break
                    turn = nxt
                else:
                    print("Неверный ход")
            except:
                print("Неверный формат")
        else:
            print("Используйте: q r s tq tr ts  или  q r s")



def main():
    print("Выберите режим:")
    print("1 - Классические шахматы")
    print("2 - Гексагональные шахматы на троих")
    choice = input("> ").strip()
    if choice == '1':
        run_chess()
    elif choice == '2':
        run_hex()
    else:
        print("Неверный выбор")

if name == "__main__":
    main()
