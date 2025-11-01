import random

class Game:
    def __init__(self, n_dim = 3):
        self.n_dim = n_dim
        self.FIELDS_COORD = []
        for i in range(n_dim):
            for j in range(n_dim):
                self.FIELDS_COORD.append((i + 1, j + 1))
        self.empty_sign = "-"
        self.zero_sign = "0"
        self.cross_sign = "X"
        self.win_conditions = self.get_win_conditions(n_dim=self.n_dim)

        self.cross_data = []
        self.zero_data = []
        self.field_template = self.get_empty_field(
            n_dim=self.n_dim,
            empty_sign=self.empty_sign
        )
        self.indices = [i for i, char in enumerate(self.field_template) if char == self.empty_sign]
        self.current_player = None
        self.current_coord = None
        self.history = {}
        self.player_fields_history = {
            f"Player {self.zero_sign}": [],
            f"Player {self.cross_sign}": [],
        }
        self.empty_coords = None

    @staticmethod
    def get_win_conditions(n_dim = 3):
        win_conditions = []
        for i in range(n_dim * n_dim):
            if (i + 1) % n_dim == 0:
                win_conditions.append(tuple(range(i + 1 - n_dim, i + 1)))
        for j in range(n_dim):
            win_conditions.append(tuple(range(j, n_dim * n_dim + j, n_dim)))

        cross_lr = [c[i] for i, c in enumerate(win_conditions[:n_dim])]
        win_conditions.append(tuple(cross_lr))

        cross_rl = [c[-(i + 1)] for i, c in enumerate(win_conditions[:n_dim])]
        win_conditions.append(tuple(cross_rl))
        return win_conditions

    @staticmethod
    def get_empty_field(n_dim = 3, empty_sign = "-"):
        head_str = f"  "
        for i in range(n_dim):
            head_str = f"{head_str}  {i + 1} "
        body_str = f"{head_str}\n"
        for i in range(n_dim):
            row_str = f"{i + 1} |"
            for _ in range(n_dim):
                row_str = f"{row_str} {empty_sign} |"
            body_str = f"{body_str}{row_str}\n"
        return body_str

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
        if len(self.player_fields_history[f"Player {self.current_player}"]) >= self.n_dim:
            for coord in self.win_conditions:
                wc = set([id_ for i, id_ in enumerate(self.FIELDS_COORD) if i in coord])
                if len(wc.intersection(set(self.player_fields_history[f"Player {self.current_player}"]))) == self.n_dim:
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
            if step > self.n_dim ** 2 + 1:
                break


if __name__ == "__main__":
    game = Game(n_dim=3)
    game.start()







