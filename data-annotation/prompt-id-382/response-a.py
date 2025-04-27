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
        self.player_hits = []
        self.computer_hits = []

        self.player_buttons = []
        self.computer_buttons = []

        self.log = tk.Text(self.window, width=30, height=20)
        self.log.grid(row=0, column=33, rowspan=16)

        self.legend = tk.Text(self.window, width=30, height=8)
        self.legend.grid(row=16, column=33)
        self.legend.insert("1.0", "Player board: Shows your ships and\ncomputer's shots\nComputer board: Shows your shots\n\nblue: your ship\ngreen: your hit\ngray: your miss\nyellow: computer hit on you\norange: computer miss")

        self.current_ship = None
        self.player_turn = False
        self.game_over = False
        self.ship_being_placed = []
        self.placing_ships = True
        self.ship_start_position = None

        tk.Label(self.window, text="Your Board").grid(row=15, column=0, columnspan=15)
        tk.Label(self.window, text="Computer's Board").grid(row=15, column=17, columnspan=15)

        for i in range(15):
            player_row = []
            computer_row = []
            for j in range(15):
                player_button = tk.Button(self.window, text="", width=2, command=lambda row=i, column=j: self.player_click(row, column))
                player_button.grid(row=i, column=j)
                player_row.append(player_button)
                
                computer_button = tk.Button(self.window, text="", width=2, command=lambda row=i, column=j: self.computer_click(row, column))
                computer_button.grid(row=i, column=j+17)
                computer_row.append(computer_button)
            self.player_buttons.append(player_row)
            self.computer_buttons.append(computer_row)

        for i in range(15):
            label = tk.Label(self.window, text=str(i+1))
            label.grid(row=i, column=15)
            label2 = tk.Label(self.window, text=str(i+1))
            label2.grid(row=i, column=32)
        for i in range(15):
            label = tk.Label(self.window, text=chr(65+i))
            label.grid(row=16, column=i)
            label2 = tk.Label(self.window, text=chr(65+i))
            label2.grid(row=16, column=i+17)

        self.ship_buttons = {}
        for i, ship in enumerate(self.player_ships):
            button = tk.Button(self.window, text=ship + " (" + str(self.player_ships[ship]) + ")", command=lambda ship=ship: self.select_ship(ship))
            button.grid(row=i, column=35)
            self.ship_buttons[ship] = button

        self.start_button = tk.Button(self.window, text="Start game", command=self.start_game)
        self.start_button.grid(row=len(self.player_ships), column=35)
        self.start_button.config(state="disabled")

        self.reset_button = tk.Button(self.window, text="Reset ships", command=self.reset_ships)
        self.reset_button.grid(row=len(self.player_ships)+1, column=35)

        self.window.mainloop()

    def select_ship(self, ship):
        self.current_ship = ship
        self.ship_being_placed = []
        self.ship_start_position = None
        self.log.insert("1.0", f"Selected {ship} for placement\n")

    def player_click(self, row, column):
        if self.game_over:
            return

        if self.placing_ships and self.current_ship and self.player_ships[self.current_ship] > 0:
            if (row, column) not in self.player_ships_placed:
                if self.ship_start_position is None:
                    self.ship_start_position = (row, column)
                    self.ship_being_placed = [(row, column)]
                    self.player_ships_placed[(row, column)] = self.current_ship
                    self.player_buttons[row][column].config(bg="blue")
                    self.player_ships[self.current_ship] -= 1
                    if self.player_ships[self.current_ship] == 0:
                        self.ship_buttons[self.current_ship].config(state="disabled")
                        self.current_ship = None
                        self.ship_start_position = None
                        if self.check_all_ships_placed():
                            self.start_button.config(state="normal")
                else:
                    if self.is_valid_placement(row, column):
                        self.ship_being_placed.append((row, column))
                        self.player_ships_placed[(row, column)] = self.current_ship
                        self.player_buttons[row][column].config(bg="blue")
                        self.player_ships[self.current_ship] -= 1
                        if self.player_ships[self.current_ship] == 0:
                            if not self.check_ship_placement(self.ship_being_placed):
                                self.log.insert("1.0", "Ship placement is incorrect, please reset\n")
                            self.ship_buttons[self.current_ship].config(state="disabled")
                            self.current_ship = None
                            self.ship_start_position = None
                            if self.check_all_ships_placed():
                                self.start_button.config(state="normal")
                    else:
                        self.log.insert("1.0", "Invalid placement position\n")

    def computer_click(self, row, column):
        if self.game_over or not self.player_turn or self.placing_ships:
            return

        if (row, column) not in self.player_hits:
            self.player_hits.append((row, column))
            if (row, column) in self.computer_ships_placed:
                self.computer_buttons[row][column].config(bg="green")
                self.log.insert("1.0", "Player hit computer ship\n")
                if self.check_sunk((row, column), self.computer_ships_placed, self.player_hits):
                    ship_name = self.computer_ships_placed[(row, column)]
                    self.log.insert("1.0", f"**Computer {ship_name} sunk**\n")
                    if self.check_win():
                        self.log.insert("1.0", "PLAYER WINS!\n")
                        self.game_over = True
            else:
                self.computer_buttons[row][column].config(bg="gray")
                self.log.insert("1.0", "Player missed\n")
            self.player_turn = False
            self.window.after(1000, self.computer_turn)

    def start_game(self):
        self.start_button.config(state="disabled")
        self.reset_button.config(state="disabled")
        for ship in self.player_ships:
            self.ship_buttons[ship].config(state="disabled")
        self.place_computer_ships()
        self.placing_ships = False
        self.player_turn = True
        self.log.insert("1.0", "Game started! Your turn\n")

    def place_computer_ships(self):
        for ship, original_length in self.computer_ships.items():
            placed = False
            while not placed:
                orientation = choice(["h", "v"])
                if orientation == "h":
                    row = randint(0, 14)
                    column = randint(0, 15-original_length)
                    positions = [(row, column+i) for i in range(original_length)]
                else:
                    row = randint(0, 15-original_length)
                    column = randint(0, 14)
                    positions = [(row+i, column) for i in range(original_length)]
                
                if self.is_valid_computer_placement(positions):
                    for pos in positions:
                        self.computer_ships_placed[pos] = ship
                    placed = True

    def is_valid_computer_placement(self, positions):
        for pos in positions:
            if pos in self.computer_ships_placed:
                return False
            for adj_pos in self.get_adjacent_positions(pos):
                if adj_pos in self.computer_ships_placed and adj_pos not in positions:
                    return False
        return True

    def get_adjacent_positions(self, pos):
        adjacent = []
        row, col = pos
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 15 and 0 <= new_col < 15:
                    adjacent.append((new_row, new_col))
        return adjacent

    def is_valid_placement(self, row, column):
        if not self.ship_start_position:
            return True
        
        start_row, start_col = self.ship_start_position
        
        if row == start_row:
            if abs(column - start_col) == len(self.ship_being_placed):
                return True
        elif column == start_col:
            if abs(row - start_row) == len(self.ship_being_placed):
                return True
        
        return False

    def computer_turn(self):
        if self.game_over:
            return
        
        while True:
            row = randint(0, 14)
            column = randint(0, 14)
            if (row, column) not in self.computer_hits:
                self.computer_hits.append((row, column))
                if (row, column) in self.player_ships_placed:
                    self.player_buttons[row][column].config(bg="yellow")
                    self.log.insert("1.0", "Computer hit player ship\n")
                    if self.check_sunk((row, column), self.player_ships_placed, self.computer_hits):
                        ship_name = self.player_ships_placed[(row, column)]
                        self.log.insert("1.0", f"**Player {ship_name} sunk**\n")
                        if self.check_computer_win():
                            self.log.insert("1.0", "COMPUTER WINS!\n")
                            self.game_over = True
                else:
                    self.player_buttons[row][column].config(bg="orange")
                    self.log.insert("1.0", "Computer missed\n")
                break
        self.player_turn = True

    def check_sunk(self, position, ships, hits):
        ship = ships[position]
        ship_positions = [pos for pos, s in ships.items() if s == ship]
        return all(pos in hits for pos in ship_positions)

    def check_ship_placement(self, positions):
        rows = [pos[0] for pos in positions]
        columns = [pos[1] for pos in positions]
        if len(set(rows)) == 1 and max(columns) - min(columns) == len(positions) - 1:
            return True
        if len(set(columns)) == 1 and max(rows) - min(rows) == len(positions) - 1:
            return True
        return False

    def check_all_ships_placed(self):
        return all(count == 0 for count in self.player_ships.values())

    def check_win(self):
        for ship_pos in self.computer_ships_placed:
            if ship_pos not in self.player_hits:
                return False
        return True

    def check_computer_win(self):
        for ship_pos in self.player_ships_placed:
            if ship_pos not in self.computer_hits:
                return False
        return True

    def reset_ships(self):
        self.player_ships_placed = {}
        self.ship_being_placed = []
        self.ship_start_position = None
        self.current_ship = None
        self.player_ships = {"Carrier": 5, "Battleship": 4, "Cruiser": 3, "Destroyer": 2, "Destroyer2": 2}
        
        for row in self.player_buttons:
            for button in row:
                button.config(bg="SystemButtonFace")
        
        for ship, button in self.ship_buttons.items():
            button.config(state="normal", text=ship + " (" + str(self.player_ships[ship]) + ")")
        
        self.start_button.config(state="disabled")
        self.log.insert("1.0", "Ships reset. Place your ships again.\n")

Battleship()