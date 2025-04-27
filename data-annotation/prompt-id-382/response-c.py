import tkinter as tk
from random import randint, choice

class Battleship:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Battleship")
        self.player_ships = {"Carrier": 5, "Battleship": 4, "Cruiser": 3, "Destroyer": 2, "Destroyer2": 2}
        self.computer_ships = {"Carrier": 5, "Battleship": 4, "Cruiser": 3, "Destroyer": 2, "Destroyer2": 2}
        self.player_ships_placed = {}
        self.computer_ships_placed = {}
        self.current_ship = None
        self.ship_being_placed = []
        self.player_turn = False
        self.game_over = False
        self.buttons_player = []
        self.buttons_computer = []
        self.log = tk.Text(self.window, width=40, height=20)
        self.log.grid(row=0, column=31, rowspan=16)
        self.legend = tk.Text(self.window, width=40, height=5)
        self.legend.grid(row=16, column=31)
        self.legend.insert("1.0", "Player board on left\nComputer board on right\nShips: blue or red\nHits: green or yellow\nMiss: gray or orange")
        self.ship_buttons = {}
        r = 0
        for ship in self.player_ships:
            b = tk.Button(self.window, text=ship, command=lambda s=ship: self.select_ship(s))
            b.grid(row=r, column=32)
            self.ship_buttons[ship] = b
            r += 1
        self.start_button = tk.Button(self.window, text="Start game", command=self.start_game)
        self.start_button.grid(row=r, column=32)
        for i in range(15):
            row_btns = []
            for j in range(15):
                b = tk.Button(self.window, width=2, command=lambda r=i, c=j: self.player_board_click(r, c))
                b.grid(row=i, column=j)
                row_btns.append(b)
            self.buttons_player.append(row_btns)
        for i in range(15):
            tk.Label(self.window, text=str(i+1)).grid(row=i, column=15)
        for j in range(15):
            tk.Label(self.window, text=chr(65+j)).grid(row=15, column=j)
        for i in range(15):
            row_btns = []
            for j in range(15):
                b = tk.Button(self.window, width=2, state="disabled", command=lambda r=i, c=j: self.computer_board_click(r, c))
                b.grid(row=i, column=j+16)
                row_btns.append(b)
            self.buttons_computer.append(row_btns)
        for i in range(15):
            tk.Label(self.window, text=str(i+1)).grid(row=i, column=30)
        for j in range(15):
            tk.Label(self.window, text=chr(65+j)).grid(row=15, column=j+16)
        self.window.mainloop()

    def select_ship(self, ship):
        self.current_ship = ship
        self.ship_being_placed = []

    def player_board_click(self, row, column):
        if self.game_over:
            return
        if not self.player_turn and self.current_ship:
            if (row, column) not in self.player_ships_placed:
                self.ship_being_placed.append((row, column))
                self.player_ships_placed[(row, column)] = self.current_ship
                self.buttons_player[row][column].config(bg="blue")
                self.player_ships[self.current_ship] -= 1
                if self.player_ships[self.current_ship] == 0:
                    if not self.check_ship_placement(self.ship_being_placed):
                        self.log.insert("1.0", "Invalid placement\n")
                    self.ship_buttons[self.current_ship].config(state="disabled")
                    self.current_ship = None
                    self.ship_being_placed = []
                if all(v == 0 for v in self.player_ships.values()):
                    self.player_turn = False

    def computer_board_click(self, row, column):
        if self.game_over or not self.player_turn:
            return
        if (row, column) in self.computer_ships_placed:
            self.buttons_computer[row][column].config(bg="green")
            self.log.insert("1.0", "Player hit computer ship\n")
            if self.check_sunk((row, column), self.computer_ships_placed):
                self.log.insert("1.0", "Computer ship sunk\n")
        else:
            self.buttons_computer[row][column].config(bg="gray")
            self.log.insert("1.0", "Player missed\n")
        self.player_turn = False
        self.computer_turn()

    def start_game(self):
        if not all(v == 0 for v in self.player_ships.values()):
            self.log.insert("1.0", "Place all ships first\n")
            return
        self.start_button.config(state="disabled")
        for s in self.ship_buttons:
            self.ship_buttons[s].config(state="disabled")
        self.place_computer_ships()
        for i in range(15):
            for j in range(15):
                self.buttons_computer[i][j].config(state="normal")
        self.player_turn = True
        self.legend.config(state="disabled")
        self.log.insert("1.0", "Game started\n")

    def place_computer_ships(self):
        for ship, length in self.computer_ships.items():
            placed = False
            while not placed:
                orientation = choice(["h", "v"])
                if orientation == "h":
                    row = randint(0, 14)
                    col = randint(0, 15 - length)
                    coords = [(row, col + i) for i in range(length)]
                else:
                    row = randint(0, 15 - length)
                    col = randint(0, 14)
                    coords = [(row + i, col) for i in range(length)]
                if all(c not in self.computer_ships_placed for c in coords):
                    for c in coords:
                        self.computer_ships_placed[c] = ship
                    placed = True
                    for r, c in coords:
                        self.buttons_computer[r][c].config(bg="red")

    def computer_turn(self):
        if self.game_over:
            return
        hit = False
        while not hit:
            row = randint(0, 14)
            col = randint(0, 14)
            if (row, col) not in self.computer_ships_placed:
                if (row, col) in self.player_ships_placed:
                    self.buttons_player[row][col].config(bg="yellow")
                    self.log.insert("1.0", "Computer hit player ship\n")
                    if self.check_sunk((row, col), self.player_ships_placed):
                        self.log.insert("1.0", "Player ship sunk\n")
                else:
                    self.buttons_player[row][col].config(bg="orange")
                    self.log.insert("1.0", "Computer missed\n")
                hit = True
        self.player_turn = True

    def check_sunk(self, position, ships):
        ship = ships[position]
        for pos, s in ships.items():
            if s == ship and pos != position:
                return False
        return True

    def check_ship_placement(self, positions):
        rows = [p[0] for p in positions]
        cols = [p[1] for p in positions]
        if len(set(rows)) == 1 and max(cols) - min(cols) == len(positions) - 1:
            return True
        if len(set(cols)) == 1 and max(rows) - min(rows) == len(positions) - 1:
            return True
        return False

Battleship()