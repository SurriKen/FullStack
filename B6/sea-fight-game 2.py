import random
from time import sleep
import numpy as np

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
        self.position = None
        self.ship_coords = None
        self.ship_cell_around = None
        self.add_status = False
        self.damage = None
        self.sink_status = False

    def get_ship_cell_around(self, field: np.ndarray) -> None:
        self.ship_cell_around = []
        for coord in self.ship_coords:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if (coord[0] + i, coord[1] + j) not in self.ship_coords and 0 <= coord[0] + i < field.shape[0] and\
                            0 <= coord[1] + j < field.shape[1] and coord not in self.ship_cell_around:
                        try:
                            _ = field[coord[0] + i, coord[1] + j]
                            self.ship_cell_around.append((coord[0] + i, coord[1] + j))
                        except:
                            continue

    def generate_coords(self, field: np.ndarray) -> bool:
        rel_coord = [(i, j) for i in range(field.shape[0] - self.lenth + 1) for j in
                     range(field.shape[1] - self.lenth + 1) if not field[(i, j)]]
        count = 0
        add_status = False
        self.ship_coords = []
        while not add_status:
            start_coord = random.choice(rel_coord)
            self.position = random.choice(["v", "h"])
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

    def check_sink(self) -> bool:
        print(self.name, self.ship_coords, self.damage)
        if sorted(self.ship_coords) == sorted(self.damage):
            self.sink_status = True
            return True
        return False

    def activate(self, field: np.ndarray) -> None:
        self.generate_coords(field)
        self.get_ship_cell_around(field)
        self.damage = []
        self.add_status = True


class Board:
    def __init__(self, n_dim = 6, ships=None, hid=True, owner: str = None):
        self.owner = owner if owner else "No owner"
        self.n_dim = n_dim
        self.hid = hid

        if ships is None:
            ships = {}
        kwarg = self.get_kwargs(ships)
        self.ships_dict = kwarg if kwarg else {3: 1, 2: 2, 1: 4}

        self.field_coord = None
        self.field_array = None
        self.dot_list = None
        self.field_template = None
        self.unused_coords = None
        self.ships_obj = None
        self.initialize_field()


    def initialize_field(self):
        self.field_coord = [(i, j) for i in range(1, self.n_dim + 1) for j in range(1, self.n_dim + 1)]
        self.field_array = np.zeros([self.n_dim, self.n_dim], dtype=int)
        self.dot_list = []
        for coord in self.field_coord:
            self.dot_list.append(Dot(coord=coord, hid=self.hid, ship_dot=False))
        self.field_template = self.get_field()
        self.unused_coords = [(i, j) for i in range(1, self.n_dim + 1) for j in range(1, self.n_dim + 1)]

    def add_ship_to_array(self, ship: Ship) -> None:
        for coord in ship.ship_coords:
            self.field_array[coord] = 2
        for coord in ship.ship_cell_around:
            self.field_array[coord] = 1

    def get_kwargs(self, kwargs: dict):
        if not isinstance(kwargs, dict):
            raise TypeError("arg 'ships' must be a dict")
        kwarg_ = {}
        for k, v in kwargs.items():
            try:
                k = int(k)
                v = int(v)
            except (TypeError, ValueError) as e:
                print(e)
                raise TypeError("arg 'ships' must be a dict of ints, where are key - lenth of ship and value - quantity of ship")
            else:
                if k <= self.n_dim:
                    kwarg_[k] = v
                else:
                    raise ValueError("Lenth of ship is larger than field")
        return kwarg_

    def get_field(self):
        dec = "" if self.n_dim < 10 else " "
        name_str = f"{self.owner}"
        while len(name_str) < 24:
            name_str = f"_{name_str}_"
        name_str = f"{dec}   {name_str}\n"
        head_str = f"{dec}  "
        for i in range(self.n_dim):
            head_str = f"{head_str}  {i + 1} "

        body_str = f"{name_str}{head_str}\n"
        count = 0
        for i in range(self.field_array.shape[0]):
            row_str = f"{dec}{i + 1} |" if i + 1 < 10 else f"{i + 1} |"

            for j in range(self.field_array.shape[1]):
                row_str = f"{row_str}{self.dot_list[count].init_dot()}|"
                count += 1
            body_str = f"{body_str}{row_str}\n"
        return body_str

    def update_dots(self):
        for i, dot in enumerate(self.dot_list):
            if self.field_array[(self.field_coord[i][0] - 1, self.field_coord[i][1] -1)] == 2:
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
                self.ships_obj = {}
                for l in ships_lenths:
                    ship = Ship(l, name=f"Ship #{count}")
                    ship.activate(self.field_array)
                    self.ships_obj[ship.name] = ship
                    self.add_ship_to_array(ship)
                    count += 1
                self.update_dots()
                break
            except:
                self.initialize_field()
                self.ship_coord = []
                x += 1
                if x > 100:
                    raise RuntimeError("Too many tries! Change ships dict or field size")

    def check_loose_status(self):
        if all([ship.sink_status for ship in self.ships_obj.values()]):
            return True
        return False

    def step(self, coord):
        idx = self.field_coord.index(coord)
        self.dot_list[idx].update_status(hid=self.hid, hit_status=True)
        self.unused_coords = [i for i in self.unused_coords if i != coord]
        if self.dot_list[idx].ship_dot:
            for ship in self.ships_obj.values():
                if (coord[0]-1, coord[1]-1) in ship.ship_coords:
                    ship.damage.append((coord[0]-1, coord[1]-1))
                    ship.check_sink()
                    break
            if ship.sink_status:
                for ac in ship.ship_cell_around:
                    id = self.field_coord.index((ac[0] + 1, ac[1] + 1))
                    self.dot_list[id].update_status(hid=self.hid, hit_status=True)
            return True
        else:
            return False


class Player:
    def __init__(self, name: str, coords: list):
        self.name = name
        self.coords = coords
        self.history = []

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
        input_coord = self.input_text()
        while True:
            if input_coord in unused_coords:
                break
            else:
                print(f"This coordinates incorrect or has already been used. \n"
                      f"Use one of these free coordinates instead {unused_coords}.\n")
                input_coord = self.input_text()
        self.history.append(input_coord)
        return input_coord


class Computer(Player):
    def step(self, unused_coords):
        input_coord = random.choice(unused_coords)
        self.history.append(input_coord)
        return input_coord


class Game:
    def __init__(self, n_dim = 6, ships=None):
        self.n_dim = n_dim
        self.ships = ships

        self.player = Player(name="Player", coords=[])
        self.player_board = Board(n_dim=n_dim, ships=ships, hid=False, owner=self.player.name)
        self.player_board.fill_board()
        self.player.coords = self.player_board.unused_coords

        self.coputer = Computer(name="Computer", coords=[])
        self.computer_board = Board(n_dim=n_dim, ships=ships, owner=self.coputer.name)
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
        # print("Welcome to Sea Fight!")
        # print("Would you like to play sea fight? (y/n)")
        # print("If you don't want to play sea fight, type 'n'")
        # print("If you want to play sea fight, type 'y'")
        # agr = input()
        agr = "y"
        if agr.lower() == "y":
            step = 1
            while True:
                if step == 1:
                    print(f"Game started!!!\n"
                          f"{self.unite_boards()}")
                print("_" * 50)
                ships_count = sum([not ship.sink_status for ship in self.current_board.ships_obj.values()])
                print(f"{self.current_player.name} step. {ships_count} ships left")
                input_coord = self.current_player.step(self.current_board.unused_coords)
                res = self.current_board.step(input_coord)
                print(f"{self.current_player.name} make a step {input_coord}", res)
                print(self.unite_boards())
                if ships_count != sum([not ship.sink_status for ship in self.current_board.ships_obj.values()]):
                    print(f"Ship has been sunk by {self.current_player.name}. "
                          f"{sum([not ship.sink_status for ship in self.current_board.ships_obj.values()])} ships left")
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
        else:
            print("Thank you for playing!")


if __name__ == "__main__":
    # new_ships = {5: 1, 4: 2, 3: 3, 2: 4, 1: 6}
    new_ships = {4: 1, 3:2, 2:4, 1:6}

    game = Game(n_dim=10, ships=new_ships)
    game.start()
    # game.step()
    # print(all([True, True, True, True, True, True]))