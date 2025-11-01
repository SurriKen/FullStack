import random
from time import sleep
import numpy as np

RED_BG = '\033[41m'
BLUE_BG = '\033[44m'
BLACK_BG = '\033[40m'
GREEN_BG = '\033[42m'
BLACK = '\033[30m'
DEFAULT = '\033[39m'
RESET = '\033[0m'

class Dot:
    def __init__(self, coord: tuple[int, int], hid: bool = True, hit_status: bool = False):
        self.hid = hid
        self.coord = coord
        self.hit_status = hit_status
        self.empty_sign = "-"
        self.miss_sign = "т"
        self.damage_sign = "X"
        self.init_dot_color = DEFAULT
        self.used_dot_color = BLACK
        self.bg_miss_color = BLUE_BG
        self.bg_damage_color = RED_BG
        if self.hid:
            self.ship_sign, self.player_sign = self.empty_sign
            self.bg_color = BLACK_BG
            self.ship_color = BLACK_BG
        else:
            self.bg_color = BLACK_BG
            self.ship_sign = "O"
            self.player_sign = "■"
            self.ship_color = GREEN_BG

    def is_in(self, ship: list) -> bool:
        return self.coord in ship

class Ship:
    def __init__(self, lenth: int):
        self.lenth = lenth
        self.position = random.choice(["v", "h"])
        self.ship_coords = None
        self.ship_cell_around = None
        self.add_status = False

    def get_ship_cell_around(self, field: np.ndarray) -> list:
        cell_around = []

        for coord in self.ship_coords:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if coord not in self.ship_coords and 0 <= coord[0] + i < field.shape[0] and\
                            0 <= coord[1] + j < field.shape[1]:
                        try:
                            _ = field[coord[0] + i, coord[1] + j]
                            cell_around.append((coord[0] + i, coord[1] + j))
                        except:
                            continue
        return cell_around

    def generate_coords(self, field: np.ndarray) -> bool:
        rel_coord = [(i, j) for i in range(field.shape[0] - self.lenth + 1) for j in
                     range(field.shape[1] - self.lenth + 1) if not field[(i, j)]]
        count = 0
        add_status = False
        self.ship_coords = []
        while not add_status:
            start_coord = random.choice(rel_coord)
            for d in self.position:
                if d == "v" and start_coord[1] + self.lenth + 1 <= field.shape[1] and \
                        not np.sum(field[start_coord[0]:start_coord[0] + self.lenth, start_coord[1]]):
                    for i in range(start_coord[0], start_coord[0] + self.lenth):
                        self.ship_coords.append((i, start_coord[1]))
                    add_status = True
                    break
                elif d == "h" and start_coord[0] + self.lenth + 1 <= field.shape[0] and \
                        not np.sum(field[start_coord[0], start_coord[1]:start_coord[1] + self.lenth]):
                    for i in range(start_coord[1], start_coord[1] + self.lenth):
                        self.ship_coords.append((start_coord[0], i))
                    add_status = True
                    break
                else:
                    continue
            count += 1
            if count > 100:
                break
        return add_status


class Board:
    def __init__(self):
        self.ships = []


class Game:
    def __init__(self, n_dim = 6, ships=None):
        if ships is None:
            ships = {}
        self.n_dim = n_dim
        kwarg = self.get_kwargs(ships)
        self.ships_dict = kwarg if kwarg else {3: 1, 2: 2, 1: 4}
        self.FIELDS_COORD = self.generate_initial_coord()

        # self.playground = np.zeros([self.n_dim, self.n_dim], dtype=int)
        self.field_with_ships = np.zeros([self.n_dim, self.n_dim], dtype=int)

        self.empty_sign = "-"
        self.miss_sign = "т"
        self.damage_sign = "X"
        self.ship_sign = "O"
        self.player_sign = "■"

        self.field_template = self.get_empty_field()
        self.indices = self.update_indices()

        self.current_player = None
        self.current_coord = None
        self.ship_full_info = {}
        self.history = {}
        self.player_fields_history = {
            f"Computer": [],
            f"Player": [],
        }
        self.empty_coords = None

    def update_indices(self):
        return [i for i, char in enumerate(self.field_template) if char == self.empty_sign]

    def winner_check(self, damage_coords):
        ship_coords = self.coord_array_to_template(self.get_ship_coord())
        if sorted(ship_coords) == sorted(damage_coords):
            return True
        return False

    def get_kwargs(self, kwargs: dict):
        if not isinstance(kwargs, dict):
            raise TypeError("kwargs must be a dict")
        kwarg_ = {}
        for k, v in kwargs.items():
            try:
                k = int(k)
                v = int(v)
            except (TypeError, ValueError) as e:
                print(e)
                raise TypeError("kwargs must be a dict of ints")
            else:
                if k <= self.n_dim:
                    kwarg_[k] = v
                else:
                    raise ValueError("Lenth of ship is larger than field")
        return kwarg_

    @property
    def get_ships(self):
        ships = []
        for s, c in self.ships_dict.items():
            for _ in range(c):
                ships.append(s)
        return sorted(ships, reverse=True)

    def get_empty_field(self):
        dec = "" if self.n_dim < 10 else " "
        head_str = f"{dec}  "
        for i in range(self.n_dim):
            head_str = f"{head_str}  {i + 1} "
        body_str = f"{head_str}\n"
        for i in range(self.n_dim):
            row_str = f"{dec}{i + 1} |" if i + 1 < 10 else f"{i + 1} |"
            for _ in range(self.n_dim):
                row_str = f"{row_str}{DEFAULT}{BLACK_BG} {self.empty_sign} {RESET}|"
            body_str = f"{body_str}{row_str}\n"
        return body_str

    def input_text(self):
        input_text = input(f"{self.current_player} input coordinates. Use format 'row column' with space between\n")
        while True:
            try:
                input_coord = tuple(map(int, input_text.split()))
                break
            except:
                print("Invalid coordinates. Please use format 'row column' with space between")
                input_text = input(f"{self.current_player} input coordinates again: \n")
        return input_coord

    def generate_initial_coord(self):
        return [(i, j) for i in range(1, self.n_dim + 1) for j in range(1, self.n_dim + 1)]

    def get_ship_coord(self):
        return [(i, j) for i in range(self.n_dim) for j in range(self.n_dim) if self.field_with_ships[(i, j)] == 2]

    @staticmethod
    def get_cell_around(coord: tuple, field: np.ndarray) -> list:
        cell_around = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if coord != (coord[0] + i, coord[1] + j) and 0 <= coord[0] + i < field.shape[0] and 0 <= coord[1] + j < field.shape[1]:
                    try:
                        _ = field[coord[0] + i, coord[1] + j]
                        cell_around.append((coord[0] + i, coord[1] + j))
                    except:
                        continue
        return cell_around

    @staticmethod
    def add_ship(ship_lenth: int, field: np.ndarray) -> list:
        direction = ["v", "h"]
        random.shuffle(direction)
        rel_coord = [(i, j) for i in range(field.shape[0] - ship_lenth + 1) for j in
                     range(field.shape[1] - ship_lenth + 1) if not field[(i, j)]]
        count = 0
        add_status = False
        cc = []
        while not add_status:
            start_coord = random.choice(rel_coord)
            for d in direction:
                if d == "v" and start_coord[1] + ship_lenth + 1 <= len(field) and \
                        not np.sum(field[start_coord[0]:start_coord[0] + ship_lenth, start_coord[1]]):
                    for i in range(start_coord[0], start_coord[0] + ship_lenth):
                        cc.append((i, start_coord[1]))
                    add_status = True
                    break
                elif d == "h" and start_coord[0] + ship_lenth + 1 <= len(field) and \
                        not np.sum(field[start_coord[0], start_coord[1]:start_coord[1] + ship_lenth]):
                    for i in range(start_coord[1], start_coord[1] + ship_lenth):
                        cc.append((start_coord[0], i))
                    add_status = True
                    break
                else:
                    continue
            count += 1
            if count > 100:
                break
        return cc

    @staticmethod
    def coord_array_to_template(coords: list) -> list:
        return [(c[0] + 1, c[1] + 1) for c in coords]

    @staticmethod
    def coord_template_to_array(coords: list) -> list:
        return [(c[0] - 1, c[1] - 1) for c in coords]

    def check_ship_status(self, damage_coord: tuple):
        for ship in self.ship_full_info.keys():
            if damage_coord in self.ship_full_info[ship]["coords"]:
                self.ship_full_info[ship]["damage"].append(damage_coord)
                if sorted(self.ship_full_info[ship]["coords"]) == sorted(self.ship_full_info[ship]["damage"]):
                    return ship
        return None

    def generate_ships(self):
        ships_lenths = self.get_ships
        count = 0
        while True:
            ship_lenth = ships_lenths[0]
            try:
                cc = self.add_ship(ship_lenth, self.field_with_ships)
            except:
                break
            cell_around = []
            if cc:
                for i in cc:
                    self.field_with_ships[i] = 2
                    ca = self.get_cell_around(i, self.field_with_ships)
                    for c in ca:
                        if c not in cell_around:
                            cell_around.append(c)
                        if not self.field_with_ships[c]:
                            self.field_with_ships[c] = 1

            count += 1
            self.ship_full_info[f"Ship {count}"] = {
                "lenth": ship_lenth,
                "coords": sorted(self.coord_array_to_template(cc)),
                "around_coords": self.coord_array_to_template(cell_around),
                "damage": [],
            }
            ships_lenths.pop(0)
            if not ships_lenths:
                break
            if count > 100:
                break

    def input_step(self):
        if self.current_player == "Computer":
            input_coord = random.choice(self.empty_coords)
        else:
            input_coord = self.input_text()
            while True:
                if input_coord in self.empty_coords:
                    break
                else:
                    print(f"This coordinates incorrect or has already been used. \n"
                          f"Use one of these free coordinates instead {self.empty_coords}.\n")
                input_coord = self.input_text()
        return input_coord

    def add_step_to_template(self, coord: tuple, field: str, sign: str):
        idx = self.FIELDS_COORD.index(coord)
        gs = self.indices[idx]
        color = '30m\033[41m' if sign == self.damage_sign else '30m\033[44m'
        txt = f"{color} {sign} "
        field = field[:gs-len(color)-1] + str(f"{txt}") + field[gs + 2:]
        return field

    def start(self):
        self.generate_ships()
        self.current_player = random.choice(list(self.player_fields_history.keys()))
        step = 1
        self.empty_coords = self.generate_initial_coord()
        damage_coord = []
        ships_count = len(self.get_ships)
        sink_ship = None
        while True:
            if step == 1:
                print(f"Game started!!!\n"
                      f"{self.field_template}")
            print("_" * 50)
            print(f"Step {step}. {ships_count} ships left")
            self.current_coord = self.input_step()
            self.empty_coords.pop(self.empty_coords.index(self.current_coord))
            if self.field_with_ships[(game.current_coord[0] - 1, game.current_coord[1] - 1)] == 2:
                result = self.damage_sign
                damage_coord.append(self.current_coord)
                sink_ship = self.check_ship_status(self.current_coord)
            else:
                result = self.miss_sign
            print(f"{self.current_player} make a step {self.current_coord}", result)
            self.field_template = self.add_step_to_template(self.current_coord, self.field_template, result)
            if sink_ship:
                ships_count -= 1
                print(f"{sink_ship} has been sunk by {self.current_player}. {ships_count} ships left")
                for ac in self.ship_full_info[sink_ship]["around_coords"]:
                    if ac in self.empty_coords:
                        self.field_template = self.add_step_to_template(ac, self.field_template, self.miss_sign)
                        self.empty_coords.pop(self.empty_coords.index(ac))
                self.ship_full_info.pop(sink_ship)
                sink_ship = None
            print(self.field_template)
            # print(self.empty_coords)

            self.history[f"Step {step}"] = (f"{self.current_player}", self.current_coord, result)
            self.player_fields_history[f"{self.current_player}"].append((self.current_coord, result))

            if self.winner_check(damage_coord):
                print("_" * 50)
                print(f"{self.current_player} wins!")
                print("_" * 50)
                break

            if result == self.miss_sign:
                self.current_player = 'Player' if self.current_player == "Computer" else "Computer"
            step += 1

            if step > self.n_dim ** 2 + 1:
                break

            sleep(1)


if __name__ == "__main__":
    # new_ships = {5: 1, 4: 2, 3: 3, 2: 4, 1: 6}
    new_ships = {4: 1, 3:2, 2:4, 1:6}
    game = Game(n_dim=10, ships=new_ships)
    game.start()
