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

        self.buttons = []

        self.log = tk.Text(self.window, width=20, height=20)
        self.log.grid(row=0, column=16, rowspan=16)

        self.legend = tk.Text(self.window, width=20, height=5)
        self.legend.grid(row=16, column=16)
        self.legend.insert("1.0", "Player ship: blue\nComputer ship: red\nPlayer hit: green\nComputer hit: yellow\nPlayer miss: gray\nComputer miss: orange")

        self.current_ship = None
        self.player_turn = True
        self.game_over = False
        self.ship_being_placed = []

        for i in range(15):
            row = []
            for j in range(15):
                button = tk.Button(self.window, text="", width=2, command=lambda row=i, column=j: self.click(row, column))
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)

        for i in range(15):
            label = tk.Label(self.window, text=str(i+1))
            label.grid(row=i, column=15)
        for i in range(15):
            label = tk.Label(self.window, text=chr(65+i))
            label.grid(row=15, column=i)

        self.ship_buttons = {}
        for i, ship in enumerate(self.player_ships):
            button = tk.Button(self.window, text=ship, command=lambda ship=ship: self.select_ship(ship))
            button.grid(row=i, column=17)
            self.ship_buttons[ship] = button

        self.start_button = tk.Button(self.window, text="Start game", command=self.start_game)
        self.start_button.grid(row=len(self.player_ships), column=17)

        self.window.mainloop()

    def select_ship(self, ship):
        self.current_ship = ship
        self.ship_being_placed = []

    def click(self, row, column):
        if self.game_over:
            return

        if self.current_ship and self.player_ships[self.current_ship] > 0:
            if (row, column) not in self.player_ships_placed:
                if self.ship_being_placed and self.check_adjacent(self.ship_being_placed[-1], (row, column)):
                    self.log.insert("1.0", "Ships must not be placed adjacent to each other\n")
                    return
                self.ship_being_placed.append((row, column))
                self.player_ships_placed[(row, column)] = self.current_ship
                self.buttons[row][column].config(bg="blue")
                self.player_ships[self.current_ship] -= 1
                if self.player_ships[self.current_ship] == 0:
                    if not self.check_ship_placement(self.ship_being_placed):
                        self.log.insert("1.0", "Ship placement is incorrect, please reset\n")
                    self.ship_buttons[self.current_ship].config(state="disabled")
                    self.current_ship = None
                    self.ship_being_placed = []

        elif self.player_turn:
            if (row, column) in self.computer_ships_placed:
                self.buttons[row][column].config(bg="green")
                self.log.insert("1.0", "Player hit computer ship\n")
                if self.check_sunk((row, column), self.computer_ships_placed):
                    self.log.insert("1.0", "**Computer ship sunk**\n")
            else:
                self.buttons[row][column].config(bg="gray")
                self.log.insert("1.0", "Player missed\n")
            self.player_turn = False
            self.computer_turn()
        else:
            self.log.insert("1.0", "Not player's turn\n")

    def start_game(self):
        self.start_button.config(state="disabled")
        for ship in self.player_ships:
            self.ship_buttons[ship].config(state="disabled")
        self.place_computer_ships()
        self.log.insert("1.0", "Game started\n")
        self.legend.config(state="disabled")

    def place_computer_ships(self):
        for ship, length in self.computer_ships.items():
            while True:
                orientation = choice(["h", "v"])
                if orientation == "h":                    row = randint(0, 14)
                    column = randint(0, 15-length)
                    if all((row, column+i) not in self.computer_ships_placed and (row, column+i) not in self.player_ships_placed and self.check_adjacent((row, column+i), (row, column+i-1)) for i in range(length)):
                        for i in range(length):
                            self.computer_ships_placed[(row, column+i)] = ship
                            self.buttons[row][column+i].config(bg="red")
                        break
                else:
                    row = randint(0, 15-length)
                    column = randint(0, 14)
                    if all((row+i, column) not in self.computer_ships_placed and (row+i, column) not in self.player_ships_placed and self.check_adjacent((row+i, column), (row+i-1, column)) for i in range(length)):
                        for i in range(length):
                            self.computer_ships_placed[(row+i, column)] = ship
                            self.buttons[row+i][column].config(bg="red")
                        break

    def computer_turn(self):
        if self.game_over:
            return
        while True:
            row = randint(0, 14)
            column = randint(0, 14)
            if (row, column) not in self.computer_ships_placed:
                if (row, column) in self.player_ships_placed:
                    self.buttons[row][column].config(bg="yellow")
                    self.log.insert("1.0", "Computer hit player ship\n")
                    if self.check_sunk((row, column), self.player_ships_placed):
                        self.log.insert("1.0", "**Player ship sunk**\n")
                else:
                    self.buttons[row][column].config(bg="orange")
                    self.log.insert("1.0", "Computer missed\n")
                break
        self.player_turn = True

    def check_sunk(self, position, ships):
        ship = ships[position]
        for pos, s in ships.items():
            if s == ship and pos != position:
                return False
        return True

    def check_adjacent(self, pos1, pos2):
        # If the positions are adjacent, return False
        if abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1:
            return False
        return True

    def check_ship_placement(self, positions):
        # Get the rows and columns of the positions
        rows = [pos[0] for pos in positions]
        columns = [pos[1] for pos in positions]
        # If the ship is horizontal
        if len(set(rows)) == 1 and max(columns) - min(columns) == len(positions) - 1:
            return True
        # If the ship is vertical
        if len(set(columns)) == 1 and max(rows) - min(rows) == len(positions) - 1:
            return True
        return False

Battleship()