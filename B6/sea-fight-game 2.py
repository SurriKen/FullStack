import random
from time import sleep


RED_BG = '\033[41m'
BLUE_BG = '\033[44m'
BLACK_BG = '\033[40m'
GREEN_BG = '\033[42m'
BLACK = '\033[30m'
BLUE = '\033[34m'
DEFAULT = '\033[39m'
RESET = '\033[0m'


class Dot:
    def __init__(self, coord: tuple[int, int], ship_dot: bool, hid: bool = True, hit_status: bool = False):
        self.name = f"Dot {coord}"
        self.ship_dot = ship_dot
        self.hid = hid
        self.coord = coord
        self.hit_status = hit_status
        self.empty_sign = "-"
        self.miss_sign = "т"
        self.damage_sign = "X"
        self.sea_sign = "O"
        self.ship_sign = "■"

    def is_in(self, ship_coord: list) -> bool:
        return self.coord in ship_coord

    def init_dot(self) -> str:
        if self.hit_status:
            txt_color = BLACK
            bg_color = RED_BG if self.ship_dot else BLUE_BG
            sign = self.damage_sign if self.ship_dot else self.miss_sign
        elif not self.hit_status and self.hid:
            txt_color = DEFAULT
            bg_color = BLACK_BG
            sign = self.empty_sign
        else:
            txt_color = BLACK if self.ship_dot else BLUE
            bg_color = GREEN_BG if self.ship_dot else BLACK_BG
            sign = self.ship_sign if self.ship_dot else self.sea_sign

        return f"{txt_color}{bg_color} {sign} {RESET}"

    def update_status(self, hid: bool, hit_status: bool) -> None:
        self.hit_status = hit_status
        self.hid = hid


class Ship:
    def __init__(self, lenth: int, name: str):
        self.name = name
        self.lenth = lenth
        self.start_dot = None
        self.position = None
        self.coords = None
        self.cell_around = None
        self.damage = None
        self.sink_status = False

    def activate(self, all_coords: list, used_coords: list) -> None:
        self.generate_coords(all_coords, used_coords)
        self.get_cell_around(all_coords)
        self.damage = []

    def generate_coords(self, all_coords: list, used_coords: list) -> None:
        max_c = 0
        for c in all_coords:
            if c[0] > max_c or c[1] > max_c:
                max_c = c[0] if c[0] > c[1] else c[1]
        free_coords = [c for c in all_coords if (c not in used_coords and
                       (c[0] <= max_c - self.lenth + 1 and c[1] < max_c - self.lenth + 1))]
        count = 0
        self.coords = []
        while True:
            self.position = None
            self.start_dot = random.choice(free_coords)
            position = ["v", "h"]
            random.shuffle(position)
            for pos in position:
                check = []
                if pos == "v":
                    self.position = pos
                    for i in range(self.start_dot[0], self.start_dot[0] + self.lenth):
                        if (i, self.start_dot[1]) not in used_coords:
                            check.append(True)
                        else:
                            check.append(False)
                    if all(check):
                        self.coords = [(i, self.start_dot[1]) for i in range(self.start_dot[0], self.start_dot[0] + self.lenth)]
                        break
                else:
                    self.position = pos
                    for i in range(self.start_dot[1], self.start_dot[1] + self.lenth):
                        if (self.start_dot[0], i) not in used_coords:
                            check.append(True)
                        else:
                            check.append(False)
                    if all(check):
                        self.coords = [(self.start_dot[0], i) for i in
                                       range(self.start_dot[1], self.start_dot[1] + self.lenth)]
                        break
            if len(self.coords) == self.lenth:
                break

            count += 1
            if count > 1000:
                break

    def get_cell_around(self, all_coords: list) -> None:
        self.cell_around = []
        max_c = 0
        for c in all_coords:
            if c[0] > max_c or c[1] > max_c:
                max_c = c[0] if c[0] > c[1] else c[1]
        for coord in self.coords:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    ac = (coord[0] + i, coord[1] + j)
                    if ac not in self.coords and 1 <= ac[0] <= max_c and 1 <= ac[1] <= max_c and ac not in self.cell_around:
                        self.cell_around.append((coord[0] + i, coord[1] + j))

    def check_sink(self) -> bool:
        if sorted(self.coords) == sorted(self.damage):
            self.sink_status = True
            return True
        return False


class Board:
    def __init__(self, n_dim: int = 6, hid: bool = True, owner: str = None):
        self.owner = owner if owner else "No owner"
        self.n_dim = self.get_n_dim(n_dim=n_dim)
        self.hid = hid
        if self.n_dim <= 8:
            self.ships_dict = {3: 1, 2: 2, 1: 4}
        elif self.n_dim <= 12:
            self.ships_dict = {4: 1, 3: 2, 2: 4, 1: 6}
        else:
            self.ships_dict = {5: 1, 4: 2, 3: 3, 2: 6, 1: 8}

        self.dot_list = None
        self.all_coords = None
        self.field_template = None
        self.unused_coords = None
        self.ships_obj = None
        self.used_coords = None
        self.initialize_field()

    @staticmethod
    def get_n_dim(n_dim: int) -> int:
        n_min, n_max = 6, 15
        if not isinstance(n_dim, int):
            raise TypeError("n_dim must be an integer")
        if n_min <= n_dim <= n_max:
            return n_dim
        elif n_dim < n_min:
            print(f"n_dim must be >= {n_min} ({n_dim}). That's why n_dim was set as {n_min}")
            return n_min
        else:
            print(f"n_dim must be <= {n_max} ({n_dim}). That's why n_dim was set as {n_max}")
            return n_max

    def initialize_field(self):
        self.dot_list = [[Dot(coord=(j, i), hid=self.hid, hit_status=False, ship_dot=False) for i in range(1, self.n_dim + 1)] for j in range(1, self.n_dim + 1)]
        self.field_template = self.get_field()
        self.unused_coords = [(i, j) for i in range(1, self.n_dim + 1) for j in range(1, self.n_dim + 1)]
        self.all_coords = [(i, j) for i in range(1, self.n_dim + 1) for j in range(1, self.n_dim + 1)]

    def get_field(self):
        head_str = "   " if self.n_dim < 10 else "   "
        for i in range(self.n_dim):
            head_str = f"{head_str} {i + 1} " if i + 1 < 10 else f"{head_str} {i + 1}"

        name_str = f"{self.owner} Map"
        while len(name_str) < len(head_str):
            name_str = f"_{name_str}_"
        name_str = f"{name_str}\n"

        body_str = f"{name_str}{head_str}\n"
        for i in range(self.n_dim):
            row_str = f" {i + 1} " if i + 1 < 10 else f"{i + 1} "
            for j in range(self.n_dim):
                row_str = f"{row_str}{self.dot_list[i][j].init_dot()}"
            body_str = f"{body_str}{row_str}\n"
        return body_str

    def update_dots(self):
        ships_coord = []
        for ship in self.ships_obj:
            if ship.coords not in ships_coord:
                ships_coord.extend(ship.coords)
        for line in self.dot_list:
            for dot in line:
                if dot.coord in ships_coord:
                    dot.ship_dot = True

    def fill_board(self):
        ships_lenths = []
        for s, c in self.ships_dict.items():
            for _ in range(c):
                ships_lenths.append(s)
        ships_lenths = sorted(ships_lenths, reverse=True)
        self.initialize_field()
        x = 1
        while True:
            try:
                count = 1
                self.ships_obj = []
                used_coords = []
                for l in ships_lenths:
                    ship = Ship(lenth=l, name=f"Ship #{count}")

                    ship.activate(all_coords=self.all_coords, used_coords=used_coords)
                    used_coords.extend(ship.coords)
                    used_coords.extend(ship.cell_around)
                    used_coords = sorted(list(set(used_coords)))

                    if not ship.coords:
                        raise ValueError(f"Ship #{count} is empty")
                    self.ships_obj.append(ship)
                    count += 1
                if len(self.ships_obj) == len(ships_lenths):
                    self.update_dots()
                    break
            except:
                self.initialize_field()
                x += 1
                if x > 1000:
                    raise RuntimeError("Too many tries! Change ships dict or field size")

    def check_loose_status(self):
        if all([ship.sink_status for ship in self.ships_obj]):
            return True
        return False

    def step(self, coord: tuple[int, int]):
        td = (coord[0]-1, coord[1]-1)
        self.dot_list[td[0]][td[1]].update_status(hid=self.hid, hit_status=True)
        self.unused_coords = [self.dot_list[i][j].coord for i in range(self.n_dim) for j in range(self.n_dim) if not self.dot_list[i][j].hit_status]
        self.used_coords = [self.dot_list[i][j].coord for i in range(self.n_dim) for j in range(self.n_dim) if self.dot_list[i][j].hit_status]
        if self.dot_list[td[0]][td[1]].ship_dot:
            for i, ship in enumerate(self.ships_obj):
                if coord in ship.coords:
                    ship.damage.append(coord)
                    ship.check_sink()
                    break
            if self.ships_obj[i].sink_status:
                for c in self.ships_obj[i].cell_around:
                    self.dot_list[c[0]-1][c[1]-1].update_status(hid=self.hid, hit_status=True)
            self.used_coords = [self.dot_list[i][j].coord for i in range(self.n_dim) for j in range(self.n_dim) if self.dot_list[i][j].hit_status]
            self.unused_coords = [self.dot_list[i][j].coord for i in range(self.n_dim) for j in range(self.n_dim) if
                                  not self.dot_list[i][j].hit_status]
            return True
        return False


class Player:
    def __init__(self, name: str, coords: list, n_dim: int):
        self.n_dim = n_dim
        self.name = name
        self.coords = coords
        self.history = []
        self.damaged = []
        self.preferences = []

    def damaged_around(self) -> list:
        pref = []
        if self.damaged:
            for coord in self.damaged:
                x, y = coord

                # направления: вверх, вниз, влево, вправо
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    # проверяем попадание в границы поля
                    if 1 <= nx <= self.n_dim and 1 <= ny <= self.n_dim and (nx, ny) not in self.history and (nx, ny) not in pref:
                        pref.append((nx, ny))
        return pref

    def input_text(self):
        input_text = input(f"{self.name} input coordinates. Use format 'row column' with space between\n")
        while True:
            try:
                input_coord = tuple(map(int, input_text.split()))
                break
            except:
                print("Invalid coordinates. Please use format 'row column' with space between")
                input_text = input(f"{self.name} input coordinates again: \n")
        return input_coord

    def step(self, unused_coords):
        pref = self.damaged_around()
        if pref:
            print(f"Coordinates {pref} has high chances to damage enemy")
        input_coord = self.input_text()
        while True:
            if input_coord in unused_coords:
                break
            else:
                print(f"This coordinates incorrect or has already been used. \n"
                      f"Use one of these free coordinates instead {unused_coords}.\n")
                input_coord = self.input_text()
        return input_coord


class Computer(Player):
    def step(self, unused_coords):
        pref = self.damaged_around()
        if pref and random.random() < 0.9:
            input_coord = random.choice(pref)
        else:
            input_coord = random.choice(unused_coords)
        return input_coord


class Game:
    def __init__(self, n_dim = 6):
        self.n_dim = n_dim

        self.player = Player(name="Player", coords=[], n_dim=self.n_dim)
        self.player_board = Board(n_dim=n_dim, hid=False, owner=self.player.name)
        self.player_board.fill_board()
        self.player.coords = self.player_board.unused_coords

        self.coputer = Computer(name="Computer", coords=[], n_dim=self.n_dim)
        self.computer_board = Board(n_dim=n_dim, owner=self.coputer.name)
        self.computer_board.fill_board()
        self.computer_board.coords = self.computer_board.unused_coords

        self.current_player = random.choice([self.player, self.coputer])
        self.current_board = self.computer_board if self.current_player.name == self.player.name else self.player_board

    def unite_boards(self):
        pl = self.player_board.get_field().split("\n")[:-1]
        cm = self.computer_board.get_field().split("\n")[:-1]
        un_field = ""
        for p, c in zip(pl, cm):
            un_field = f"{un_field}{p}{' '*10}{c}\n"
        return un_field

    def next_player(self, damage_status: bool):
        if not damage_status:
            self.current_player = self.coputer if self.current_player.name == self.player.name else self.player
            self.current_board = self.computer_board if self.current_player.name == self.player.name else self.player_board

    def start(self):
        step = 1
        while True:
            if step == 1:
                print(f"Game started!!!\n"
                      f"{self.unite_boards()}")
            print("_" * 50)
            ships_count = sum([not ship.sink_status for ship in self.current_board.ships_obj])
            print(f"{self.current_player.name} step. {ships_count} ships left")
            input_coord = self.current_player.step(self.current_board.unused_coords)
            res = self.current_board.step(input_coord)

            if res:
                self.current_player.damaged.append(input_coord)
            self.current_player.history = self.current_board.used_coords

            print(f"{self.current_player.name} make a step {input_coord}", res)
            print(self.unite_boards())

            if ships_count != sum([not ship.sink_status for ship in self.current_board.ships_obj]):
                print(f"Ship has been sunk by {self.current_player.name}. "
                      f"{sum([not ship.sink_status for ship in self.current_board.ships_obj])} ships left")

            if self.current_board.check_loose_status():
                print("_" * 50)
                print(f"{self.current_player.name} wins!")
                print("_" * 50)
                break

            step += 1
            self.next_player(res)

            if step > 2 * self.n_dim ** 2 + 1:
                break
            sleep(1)


if __name__ == "__main__":
    game = Game(n_dim=10)
    game.start()
