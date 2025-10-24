1
import random

class Game:
    def __init__(self):
        self.FIELDS_COORD = (
            (1, 1), (1, 2), (1, 3),
            (2, 1), (2, 2), (2, 3),
            (3, 1), (3, 2), (3, 3),
        )
        self.empty_sign = "-"
        self.zero_sign = "0"
        self.cross_sign = "X"
        self.win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                               (0, 3, 6), (1, 4, 7), (2, 5, 8),
                               (0, 4, 8), (2, 4, 6)]
        self.cross_data = []
        self.zero_data = []
        self.field_template = f"    1   2   3 \n1 | - | - | - |\n2 | - | - | - |\n3 | - | - | - |"
        self.indices = [i for i, char in enumerate(self.field_template) if char == self.empty_sign]
        self.current_player = None
        self.current_coord = None
        self.history = {}
        self.player_fields_history = {
            f"Player {self.zero_sign}": [],
            f"Player {self.cross_sign}": [],
        }
        self.empty_coords = None

    def input_text(self):
        input_text = input(f"Player {self.current_player} input coordinates. Use format 'row column' with space between\n")
        while True:
            try:
                input_coord = tuple(map(int, input_text.split()))
                break
            except:
                print("Invalid coordinates. Please use format 'row column' with space between")
                input_text = input(f"Player {self.current_player} input coordinates again: \n")
        return input_coord

    def input_step(self):
        input_coord = self.input_text()
        while True:
            if input_coord in self.empty_coords:
                break
            else:
                print(f"This coordinates incorrect or has already been used. \n"
                      f"Use one of these free coordinates instead {self.empty_coords}.\n")
            input_coord = self.input_text()
        return input_coord

    def winner_check(self):
        if len(self.player_fields_history[f"Player {self.current_player}"]) >= 3:
            for coord in self.win_conditions:
                wc = set([id_ for i, id_ in enumerate(self.FIELDS_COORD) if i in coord])
                # print("wc", wc, coord, set(self.player_fields[f"Player {self.current_player}"]))
                if len(wc.intersection(set(self.player_fields_history[f"Player {self.current_player}"]))) == 3:
                    return True
        return False

    def add_step_to_template(self):
        gs = self.indices[self.FIELDS_COORD.index(self.current_coord)]
        self.field_template = self.field_template[:gs] + str(self.current_player) + self.field_template[gs + 1:]

    def start(self):
        self.current_player = random.choice([self.zero_sign, self.cross_sign])
        step = 1
        self.empty_coords = list(self.FIELDS_COORD)
        while True:
            if step == 1:
                print(f"Game started!!!\n"
                      f"{self.field_template}")
            print("_" * 50)
            print(f"Step {step}")
            self.current_coord = self.input_step()
            self.empty_coords.pop(self.empty_coords.index(self.current_coord))
            self.add_step_to_template()
            print(self.field_template)

            self.history[f"Step {step}"] = (f"Player {self.current_player}", self.current_coord)
            self.player_fields_history[f"Player {self.current_player}"].append(self.current_coord)

            if self.winner_check():
                print("_" * 50)
                print(f"Player {self.current_player} wins!")
                print("_" * 50)
                break
            self.current_player = self.zero_sign if self.current_player == self.cross_sign else self.cross_sign
            step += 1

            if not self.empty_coords:
                print("_" * 50)
                print(f"Players has a draw!!! Nobody wins, nobody lost!")
                print("_" * 50)
                break
            if step > 10:
                break


if __name__ == "__main__":
    game = Game()
    # game.current_player = random.choice([game.zero_sign, game.cross_sign])
    # game.empty_coords = list(game.FIELDS_COORD)
    # game.current_coord = game.input_step()
    # current_ind = game.FIELDS_COORD.index(game.current_coord)
    # print(game.current_coord, game.FIELDS_COORD.index(game.current_coord))
    # game.add_step_to_template()
    # print(game.field_template)
    game.start()
    print(game.history)
    print(game.player_fields_history)
    # xxx = {(1, 1), (3, 2), (3, 3)}
    # yyy = {(1, 1), (1, 2), (2, 2)}
    # print(xxx.intersection(yyy))



