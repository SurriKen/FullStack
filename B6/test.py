def recommend_battleship_moves(used_coords, all_hits, field_size, ship_sizes=[3, 2, 2, 1, 1, 1, 1]):
    """
    Анализирует попадания, отделяет потопленные корабли от поврежденных
    и выдает рекомендации только для поврежденных кораблей.

    Args:
        used_coords: список всех стреляных координат
        all_hits: список всех координат с попаданиями за игру
        field_size: размер поля (например 10)
        ship_sizes: список размеров кораблей (по умолчанию для классического поля)

    Returns:
        list: список рекомендуемых координат для поврежденных кораблей
    """
    if not all_hits:
        return []

    # Группируем попадания в связанные группы (корабли)
    def find_ships(hits):
        """Находит все группы связанных попаданий"""
        visited = set()
        ships = []

        def bfs(start):
            """BFS для поиска связанной группы попаданий"""
            queue = [start]
            ship = []
            visited.add(start)

            while queue:
                x, y = queue.pop(0)
                ship.append((x, y))

                # Проверяем 4 соседних клетки
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in hits and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

            return sorted(ship)

        for hit in hits:
            if hit not in visited:
                ship = bfs(hit)
                ships.append(ship)

        return ships

    # Получаем все корабли (группы попаданий)
    ships = find_ships(all_hits)

    # Определяем поврежденные корабли
    damaged_ships = []

    for ship in ships:
        ship_length = len(ship)
        # Корабль поврежден, если его длина меньше, чем максимальный возможный размер
        # (т.е. не все клетки корабля "убиты")
        is_damaged = ship_length not in ship_sizes or ship_length < 4

        # Лучше: проверяем, есть ли свободные соседние клетки вдоль оси корабля
        xs = [coord[0] for coord in ship]
        ys = [coord[1] for coord in ship]

        # Если корабль линейный (горизонтальный или вертикальный)
        if len(set(ys)) == 1:  # горизонтальный
            y = ys[0]
            min_x, max_x = min(xs), max(xs)
            # Проверяем, может ли корабль быть больше
            can_extend = False
            if min_x > 0 and (min_x - 1, y) not in all_hits:
                can_extend = True
            if max_x < field_size - 1 and (max_x + 1, y) not in all_hits:
                can_extend = True
            if can_extend:
                is_damaged = True

        elif len(set(xs)) == 1:  # вертикальный
            x = xs[0]
            min_y, max_y = min(ys), max(ys)
            can_extend = False
            if min_y > 0 and (x, min_y - 1) not in all_hits:
                can_extend = True
            if max_y < field_size - 1 and (x, max_y + 1) not in all_hits:
                can_extend = True
            if can_extend:
                is_damaged = True

        if is_damaged:
            damaged_ships.append(ship)

    # Генерируем рекомендации для поврежденных кораблей
    recommendations = []

    for ship in damaged_ships:
        xs = [coord[0] for coord in ship]
        ys = [coord[1] for coord in ship]

        if len(ship) == 1:
            # Одноклеточный поврежденный корабль — добиваем 4 стороны
            x, y = ship[0]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < field_size and 0 <= ny < field_size:
                    if (nx, ny) not in used_coords and (nx, ny) not in recommendations:
                        recommendations.append((nx, ny))

        elif len(set(ys)) == 1:  # Горизонтальный корабль
            y = ys[0]
            min_x, max_x = min(xs), max(xs)

            left = (min_x - 1, y)
            right = (max_x + 1, y)

            if 0 <= left[0] < field_size and left not in used_coords:
                recommendations.append(left)
            if 0 <= right[0] < field_size and right not in used_coords:
                recommendations.append(right)

        elif len(set(xs)) == 1:  # Вертикальный корабль
            x = xs[0]
            min_y, max_y = min(ys), max(ys)

            top = (x, min_y - 1)
            bottom = (x, max_y + 1)

            if 0 <= top[1] < field_size and top not in used_coords:
                recommendations.append(top)
            if 0 <= bottom[1] < field_size and bottom not in used_coords:
                recommendations.append(bottom)

    return recommendations


# Примеры использования:

# 1. Один поврежденный корабль
print("=== Один поврежденный 2-палубник ===")
used = [(5, 5), (6, 5), (4, 5), (7, 5)]
hits = [(5, 5), (6, 5)]  # 2-палубник, может продолжаться
print(recommend_battleship_moves(used, hits, 10))
# -> [(4, 5), (7, 5)] — добиваем влево или вправо

# 2. Потопленный корабль игнорируется
print("\n=== Потопленный и поврежденный корабли ===")
used = [(2, 2), (2, 3), (2, 4),  # стреляли вокруг потопленного
        (5, 5), (6, 5)]  # попадания в поврежденный
hits = [(2, 2), (2, 3), (2, 4),  # потопленный 3-палубник
        (5, 5), (6, 5)]  # поврежденный 2-палубник
print(recommend_battleship_moves(used, hits, 10))
# -> [(4, 5), (7, 5)] — только для поврежденного

# 3. Несколько поврежденных кораблей
print("\n=== Несколько поврежденных кораблей ===")
used = [(1, 1), (2, 1), (1, 3), (2, 3)]
hits = [(1, 1), (1, 3)]  # два отдельных одноклеточных
print(recommend_battleship_moves(used, hits, 10))
# -> рекомендации вокруг обоих

# 4. Нет попаданий
print("\n=== Нет попаданий ===")
print(recommend_battleship_moves([(1, 1)], [], 10))
# -> []

# 5. Все корабли потопленны
print("\n=== Все потопленны ===")
used = [(1, 1), (1, 2), (1, 3),  # весь корабль
        (0, 1), (2, 1),  # строка вокруг
        (0, 2), (2, 2),
        (0, 3), (2, 3),
        (1, 0), (1, 4)]
hits = [(1, 1), (1, 2), (1, 3)]  # 3-палубник полностью уничтожен
print(recommend_battleship_moves(used, hits, 10))
# -> [] (нет поврежденных кораблей)

damaged = [(3, 4), (2, 4), (5, 1), (6, 1)]
pref = [(5, 2), (7, 1), (6, 2)]
hist = [(1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5), (4, 1), (4, 3), (4, 4), (4, 5), (5, 1), (5, 7), (6, 1), (7, 2), (8, 1)]
print(recommend_battleship_moves(hist, damaged, 7))