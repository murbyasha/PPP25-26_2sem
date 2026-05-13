import itertools
import functools
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# ----------------------------------------------------------------------
# Вспомогательные геометрические функции
# ----------------------------------------------------------------------
def polygon_area(poly):
    """Площадь полигона (формула Гаусса)"""
    area = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0

def polygon_perimeter(poly):
    """Периметр полигона"""
    perim = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1) % n]
        perim += math.hypot(x2 - x1, y2 - y1)
    return perim

def polygon_sides(poly):
    """Генератор длин сторон полигона"""
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1) % n]
        yield math.hypot(x2 - x1, y2 - y1)

def polygon_angles(poly):
    """Возвращает координаты вершин (углов) полигона"""
    return poly

def point_in_polygon(point, poly):
    """Проверка принадлежности точки полигону (используем matplotlib.path.Path)"""
    path = Path(poly)
    return path.contains_points([point])[0]

def is_convex(poly):
    """Проверка выпуклости полигона. Выпуклый, если все повороты одного знака."""
    n = len(poly)
    if n < 3:
        return False
    sign = None
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i+1) % n]
        x2, y2 = poly[(i+2) % n]
        cross = (x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)
        if cross != 0:
            if sign is None:
                sign = cross > 0
            elif (cross > 0) != sign:
                return False
    return True

def distance(p1, p2=(0,0)):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

# ----------------------------------------------------------------------
# 1. Визуализация (ИСПРАВЛЕННАЯ)
# ----------------------------------------------------------------------
def plot_polygons(polygons, n, ax=None, color='blue', alpha=0.5, title='', equal_aspect=True):
    """Отображает n полигонов из итератора на объекте Axes ax."""
    if ax is None:
        ax = plt.gca()
    
    for i, poly in enumerate(itertools.islice(polygons, n)):
        # Если color - список, берём цвет по индексу, иначе используем один цвет
        if isinstance(color, list):
            current_color = color[i % len(color)]
        else:
            current_color = color
        
        patch = patches.Polygon(poly, closed=True, facecolor=current_color, 
                                alpha=alpha, edgecolor='black')
        ax.add_patch(patch)
    
    if equal_aspect:
        ax.set_aspect('equal')
    ax.set_title(title)
    ax.autoscale_view()

# ----------------------------------------------------------------------
# 2. Генераторы бесконечных последовательностей
# ----------------------------------------------------------------------
def gen_rectangle(w=1.0, h=0.6, step_x=1.2):
    """Бесконечная последовательность прямоугольников шириной w, высотой h,
       размещённых с шагом step_x вдоль оси X (центры на y=0)."""
    cnt = itertools.count()
    for i in cnt:
        cx = i * step_x
        yield (
            (cx - w/2, -h/2),
            (cx + w/2, -h/2),
            (cx + w/2,  h/2),
            (cx - w/2,  h/2)
        )

def gen_triangle(side=0.8, step_x=1.2):
    """Бесконечная последовательность равносторонних треугольников (вершина вверх).
       Центры на y=0, шаг step_x."""
    height = side * math.sqrt(3) / 2
    cnt = itertools.count()
    for i in cnt:
        cx = i * step_x
        yield (
            (cx, height/2),                 # верхняя вершина
            (cx - side/2, -height/2),       # левая нижняя
            (cx + side/2, -height/2)        # правая нижняя
        )

def gen_hexagon(radius=0.5, step_x=1.2):
    """Бесконечная последовательность правильных шестиугольников,
       вписанных в окружность радиуса radius, центры на y=0."""
    cnt = itertools.count()
    for i in cnt:
        cx = i * step_x
        angles = [2 * math.pi * k / 6 for k in range(6)]
        vertices = [(cx + radius * math.cos(a), radius * math.sin(a)) for a in angles]
        yield tuple(vertices)

# ----------------------------------------------------------------------
# 3. Трансформации (фабрики функций)
# ----------------------------------------------------------------------
def tr_translate(dx, dy):
    """Параллельный перенос на (dx, dy)."""
    return lambda poly: tuple((x+dx, y+dy) for x, y in poly)

def tr_rotate(angle):
    """Поворот на угол angle (в радианах) относительно начала координат."""
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return lambda poly: tuple(
        (x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in poly
    )

def tr_symmetry(axis='x'):
    """Отражение относительно оси 'x' или 'y'."""
    if axis == 'x':
        return lambda poly: tuple((x, -y) for x, y in poly)
    elif axis == 'y':
        return lambda poly: tuple((-x, y) for x, y in poly)
    else:
        raise ValueError("axis must be 'x' or 'y'")

def tr_homothety(scale, center=(0,0)):
    """Гомотетия с коэффициентом scale относительно точки center."""
    cx, cy = center
    return lambda poly: tuple(
        (cx + (x - cx) * scale, cy + (y - cy) * scale) for x, y in poly
    )

# ----------------------------------------------------------------------
# 5. Фильтры (предикаты)
# ----------------------------------------------------------------------
def flt_convex_polygon(poly):
    return is_convex(poly)

def flt_angle_point(point):
    """Возвращает предикат: есть ли вершина, точно совпадающая с point."""
    px, py = point
    return lambda poly: any(x == px and y == py for x, y in poly)

def flt_square(max_area):
    """Возвращает предикат: площадь полигона < max_area."""
    return lambda poly: polygon_area(poly) < max_area

def flt_short_side(max_len):
    """Возвращает предикат: длина кратчайшей стороны < max_len."""
    return lambda poly: min(polygon_sides(poly)) < max_len

def flt_point_inside(point):
    """Возвращает предикат: point лежит внутри полигона (только для выпуклых корректно)."""
    return lambda poly: point_in_polygon(point, poly)

def flt_polygon_angles_inside(target_poly):
    """Возвращает предикат: хотя бы одна вершина target_poly лежит внутри проверяемого полигона."""
    def predicate(poly):
        return any(point_in_polygon(p, poly) for p in target_poly)
    return predicate

def polylines_intersect(poly1, poly2):
    """Проверяет, пересекаются ли два полигона (или один внутри другого).
       Используем matplotlib.path.Path.intersects_path."""
    path1 = Path(poly1)
    path2 = Path(poly2)
    return path1.intersects_path(path2, filled=True)

# ----------------------------------------------------------------------
# 7. Декораторы (применяются к функциям-генераторам последовательностей полигонов)
# ----------------------------------------------------------------------
def make_filter_decorator(predicate):
    """Создаёт декоратор, который фильтрует выход генератора."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return filter(predicate, func(*args, **kwargs))
        return wrapper
    return decorator

def make_transform_decorator(transform):
    """Создаёт декоратор, который применяет transform ко всем полигонам."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return map(transform, func(*args, **kwargs))
        return wrapper
    return decorator

# Декораторы на основе фильтров
flt_convex_decorator = make_filter_decorator(flt_convex_polygon)
flt_short_side_decorator = lambda max_len: make_filter_decorator(flt_short_side(max_len))
flt_square_decorator = lambda max_area: make_filter_decorator(flt_square(max_area))
flt_point_inside_decorator = lambda point: make_filter_decorator(flt_point_inside(point))

# Декораторы трансформаций
tr_translate_decorator = lambda dx, dy: make_transform_decorator(tr_translate(dx, dy))
tr_rotate_decorator = lambda angle: make_transform_decorator(tr_rotate(angle))
tr_symmetry_decorator = lambda axis: make_transform_decorator(tr_symmetry(axis))
tr_homothety_decorator = lambda scale, center=(0,0): make_transform_decorator(tr_homothety(scale, center))

# ----------------------------------------------------------------------
# 9. Агрегирующие функции для reduce
# ----------------------------------------------------------------------
def agr_origin_nearest(poly_seq):
    """Возвращает ближайшую к началу координат вершину среди всех полигонов последовательности."""
    all_vertices = itertools.chain.from_iterable(poly_seq)
    return functools.reduce(lambda best, v: v if distance(v) < distance(best) else best, all_vertices)

def agr_max_side(poly_seq):
    """Возвращает длину самой длинной стороны среди всех полигонов."""
    all_sides = itertools.chain.from_iterable(polygon_sides(p) for p in poly_seq)
    return functools.reduce(lambda a, b: a if a > b else b, all_sides, 0.0)

def agr_min_area(poly_seq):
    """Возвращает минимальную площадь полигона в последовательности."""
    areas = map(polygon_area, poly_seq)
    return functools.reduce(lambda a, b: a if a < b else b, areas)

def agr_perimeter(poly_seq):
    """Суммарный периметр всех полигонов."""
    return functools.reduce(lambda s, p: s + polygon_perimeter(p), poly_seq, 0.0)

def agr_area(poly_seq):
    """Суммарная площадь всех полигонов."""
    return functools.reduce(lambda s, p: s + polygon_area(p), poly_seq, 0.0)

# ----------------------------------------------------------------------
# 8. zip_polygons
# ----------------------------------------------------------------------
def zip_polygons(*iterators):
    """Склеивает полигоны из нескольких итераторов в один полигон = конкатенация вершин."""
    return map(lambda polys: functools.reduce(lambda a, b: a + b, polys), zip(*iterators))

# ======================================================================
# ДЕМОНСТРАЦИЯ
# ======================================================================
def demo():
    # ---------- Пункт 2: Генерация и визуализация семи фигур трёх типов ----------
    print("Демонстрация п.2: 7 фигур каждого типа")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    plot_polygons(gen_rectangle(), 7, ax=axes[0], color='skyblue', title='Прямоугольники')
    plot_polygons(gen_triangle(), 7, ax=axes[1], color='lightgreen', title='Треугольники')
    plot_polygons(gen_hexagon(), 7, ax=axes[2], color='plum', title='Шестиугольники')
    plt.tight_layout()
    plt.show()

    # ---------- Пункт 4: Визуализация трансформаций ----------
    print("Демонстрация п.4: Трансформации")
    # -- 4а. Три параллельные «ленты» под острым углом
    angle = math.radians(20)
    base_rectangles = gen_rectangle(w=0.8, h=0.4, step_x=1.0)
    rot = tr_rotate(angle)
    shift1 = tr_translate(0, 0)
    shift2 = tr_translate(0, 1.2)
    shift3 = tr_translate(0, -1.2)
    
    lenta1 = map(lambda p: shift1(rot(p)), base_rectangles)
    lenta2 = map(lambda p: shift2(rot(p)), base_rectangles)
    lenta3 = map(lambda p: shift3(rot(p)), base_rectangles)

    fig, ax = plt.subplots(figsize=(8, 6))
    plot_polygons(lenta1, 5, ax=ax, color='red', alpha=0.4, title='Три параллельные ленты')
    plot_polygons(lenta2, 5, ax=ax, color='green', alpha=0.4)
    plot_polygons(lenta3, 5, ax=ax, color='blue', alpha=0.4)
    plt.show()

    # -- 4б. Две пересекающиеся ленты
    base_rects = itertools.islice(gen_rectangle(w=0.6, h=0.3, step_x=1.0), 8)
    ang1 = math.radians(30)
    ang2 = math.radians(-30)
    rot_pos = tr_rotate(ang1)
    rot_neg = tr_rotate(ang2)
    trans = tr_translate(1.5, 1.0)
    
    lenta_a = map(lambda p: trans(rot_pos(p)), base_rects)
    base_rects2 = itertools.islice(gen_rectangle(w=0.6, h=0.3, step_x=1.0), 8)
    lenta_b = map(lambda p: trans(rot_neg(p)), base_rects2)

    fig, ax = plt.subplots(figsize=(8, 6))
    plot_polygons(lenta_a, 8, ax=ax, color='orange', alpha=0.6, title='Две пересекающиеся ленты')
    plot_polygons(lenta_b, 8, ax=ax, color='purple', alpha=0.6)
    plt.show()

    # -- 4в. Две параллельные ленты треугольников, симметричных
    base_tri = gen_triangle(side=0.7, step_x=1.0)
    sym = tr_symmetry('x')
    trans_tri = tr_translate(0, 1.5)
    trans_down = tr_translate(0, -1.5)
    
    lenta_tri1 = map(trans_tri, base_tri)
    base_tri2 = gen_triangle(side=0.7, step_x=1.0)
    lenta_tri2_down = map(lambda p: trans_down(sym(p)), base_tri2)

    fig, ax = plt.subplots(figsize=(8, 6))
    plot_polygons(lenta_tri1, 6, ax=ax, color='gold', alpha=0.6, title='Две параллельные ленты треугольников, симметричных')
    plot_polygons(lenta_tri2_down, 6, ax=ax, color='darkblue', alpha=0.6)
    plt.show()

    # -- 4г. Четырёхугольники в разном масштабе
    min_angle = math.radians(10)
    max_angle = math.radians(40)
    squares = gen_rectangle(w=1.0, h=1.0, step_x=0.0)
    base_square = next(squares)
    
    scales = [0.2 * i for i in range(1, 30)]
    scaled = map(lambda s: tr_homothety(s, (0,0))(base_square), scales)
    
    def in_sector(poly):
        for x, y in poly:
            if x == 0 and y == 0:
                continue
            ang = math.atan2(y, x) % (2*math.pi)
            if not (min_angle <= ang <= max_angle):
                return False
        return True
    
    scaled_in_sector = filter(in_sector, scaled)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_polygons(scaled_in_sector, 10, ax=ax, color='teal', alpha=0.7,
                  title='Четырёхугольники в секторе между 10° и 40°')
    r = 5
    ax.plot([0, r*math.cos(min_angle)], [0, r*math.sin(min_angle)], 'k--')
    ax.plot([0, r*math.cos(max_angle)], [0, r*math.sin(max_angle)], 'k--')
    plt.show()

    # ---------- Пункт 6: Применение фильтров ----------
    print("Демонстрация п.6")
    
    @flt_short_side_decorator(1.0)
    @tr_rotate_decorator(math.radians(30))
    @tr_translate_decorator(1.5, 1.0)
    def decorated_rects():
        return gen_rectangle(w=0.6, h=0.3, step_x=1.0)
    
    filtered_6 = itertools.islice(decorated_rects(), 6)
    fig, ax = plt.subplots(figsize=(8, 6))
    plot_polygons(filtered_6, 6, ax=ax, color='crimson', title='6 фигур после фильтрации (короткая сторона < 1.0)')
    plt.show()

    # 6.2 из ≥ 15 фигур разного масштаба отобрать ≤ 4 с кратчайшей стороной меньше заданного значения
    # Используем меньшие масштабы, чтобы были фигуры с маленькими сторонами
    all_scaled = map(lambda s: tr_homothety(s, (0,0))(base_square), 
                     [0.1 + 0.05*i for i in range(20)])  # масштабы от 0.1 до 1.05
    short_side_limit = 0.4
    filtered_small_side = filter(flt_short_side(short_side_limit), all_scaled)
    limited = list(itertools.islice(filtered_small_side, 4))

    print(f"Найдено фигур с короткой стороной < {short_side_limit}: {len(limited)}")
    if len(limited) > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        plot_polygons(iter(limited), len(limited), ax=ax, color='navy', 
                      title=f'≤4 фигуры с кратчайшей стороной < {short_side_limit}')
        plt.show()
    else:
        print("Не найдено фигур, удовлетворяющих условию")

    # 6.3 из ≥ 15 пересекающихся фигур отфильтровать непересекающиеся
    base = gen_rectangle(w=1.0, h=0.5, step_x=0.0)
    many = []
    for i, sq in enumerate(itertools.islice(base, 20)):
        angle = i * 0.3
        sq_rot = tr_rotate(angle)(sq)
        trans = tr_translate(i * 0.15, 0)(sq_rot)
        many.append(trans)
    
    def flt_non_intersecting(seq):
        kept = []
        for poly in seq:
            if not any(polylines_intersect(poly, other) for other in kept):
                kept.append(poly)
                yield poly
    
    filtered_non_intersect = flt_non_intersecting(many)
    non_intersect_list = list(filtered_non_intersect)
    print(f"После удаления пересечений осталось {len(non_intersect_list)} фигур")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    plot_polygons(iter(non_intersect_list), len(non_intersect_list), ax=ax, color='teal',
                  title='Непересекающиеся из 20 исходно пересекающихся')
    plt.show()

    # ---------- Пункт 8: Агрегации ----------
    print("Демонстрация п.9: агрегирующие функции")
    test_polys = list(itertools.islice(gen_rectangle(w=1.0, h=0.5, step_x=1.5), 5))
    p1, p2, p3, p4, p5 = itertools.tee(test_polys, 5)

    nearest = agr_origin_nearest(p1)
    max_side = agr_max_side(p2)
    min_area = agr_min_area(p3)
    sum_perim = agr_perimeter(p4)
    sum_area = agr_area(p5)
    
    print(f"Ближайшая к (0,0) вершина: {nearest}")
    print(f"Максимальная длина стороны: {max_side:.3f}")
    print(f"Минимальная площадь: {min_area:.3f}")
    print(f"Суммарный периметр: {sum_perim:.3f}")
    print(f"Суммарная площадь: {sum_area:.3f}")

    # ---------- Пункт 9: zip_polygons ----------
    print("Демонстрация zip_polygons")
    it1 = [((1, 1), (2, 2), (3, 1)), ((11, 11), (12, 12), (13, 11))]
    it2 = [((1, -1), (2, -2), (3, -1)), ((11, -11), (12, -12), (13, -11))]
    zipped = list(zip_polygons(it1, it2))
    print("Результат zip_polygons:")
    for poly in zipped:
        print(poly)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    # Исправляем: передаём список цветов для разных полигонов
    plot_polygons(iter(zipped), len(zipped), ax=ax, color=['magenta', 'cyan'],
                  title='zip_polygons: склеенные треугольники', equal_aspect=True)
    plt.show()

if __name__ == "__main__":
    demo()
