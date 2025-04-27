import tkinter as tk
from random import randint, choice

# Bullet list of issues and fixes:
# *   **Game starts immediately / No distinct placement phase:** The `start_game` function was called without waiting for player placement.
#     *   **Fix:** Introduced game states (`PLACING_SHIPS`, `PLAYER_TURN`, `COMPUTER_TURN`, `GAME_OVER`). The `start_game` function now transitions the state only after validation. Clicking the grid performs placement or attacks based on the state.
# *   **Missing separate boards:** Only one grid was created.
#     *   **Fix:** Created two `tk.Frame` widgets, one for the player's grid (`player_frame`) and one for the computer's grid (`computer_frame`). Each frame contains its own set of buttons (`player_buttons`, `computer_buttons`). Labels A-J and 1-10 added for both grids.
# *   **Incorrect Ship Placement Logic:** Player ship placement was done cell-by-cell, didn't validate adjacency correctly, and didn't enforce ship length or contiguity properly before finalizing. `player_ships` dict was incorrectly used to track segments placed instead of ships remaining to be placed.
#     *   **Fix:** Implemented `place_player_ship` method. Player selects ship type, orientation, and clicks the top-left cell. The method calculates all cells, validates (bounds, overlap, adjacency), and places the entire ship at once. `player_ships_to_place` dictionary tracks ships yet to be placed. Adjacency check (`is_placement_valid`) now correctly checks neighbors against existing ships.
# *   **Computer ships visible:** Computer ships were colored red immediately upon placement.
#     *   **Fix:** `place_computer_ships` now only stores ship locations in `computer_ships_placed` dictionary and does not change button colors on the computer's grid.
# *   **Incorrect hit/miss/sunk logic:** `click` handled both placement and attacks. `check_sunk` logic was flawed. Hit tracking was missing. Computer could attack the same spot.
#     *   **Fix:** Created `attack_computer` method bound to computer grid buttons. Implemented separate hit/miss tracking sets (`player_hits`, `computer_hits`, `player_misses`, `computer_misses`). `check_sunk` now correctly checks if all parts of a ship are in the relevant `hits` set. Computer tracks guesses in `computer_guesses`.
# *   **No Adjacency Rule Enforcement:** The `check_adjacent` function was misused and didn't prevent ships from being placed next to each other.
#     *   **Fix:** Implemented `get_neighbors` and modified `is_placement_valid` to check if any cell of the new ship or its direct neighbors overlap with existing ships or their neighbors, enforcing a one-cell buffer.
# *   **No Game Over Condition:** The game did not detect when all ships of a player were sunk.
#     *   **Fix:** Implemented `check_game_over` function, called after each hit, which checks if all ships of either player are sunk and updates the game state accordingly.
# *   **UI Layout:** The layout needed adjustment for two boards. Grid size was 15x15, changed to standard 10x10.
#     *   **Fix:** Used `grid` layout manager to position the two frames, labels, log, legend, and controls. Changed `GRID_SIZE` to 10.


class Battleship:
    GRID_SIZE = 10
    SHIP_LENGTHS = {"Carrier": 5, "Battleship": 4, "Cruiser": 3, "Destroyer": 2, "Destroyer2": 2}
    PLAYER_BOARD_BG = "lightcyan"
    COMPUTER_BOARD_BG = "white"
    PLACED_SHIP_COLOR = "blue"
    HIT_COLOR_PLAYER = "yellow" # Computer hit player
    HIT_COLOR_COMPUTER = "green"  # Player hit computer
    MISS_COLOR_PLAYER = "orange" # Computer missed player
    MISS_COLOR_COMPUTER = "gray" # Player missed computer

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Battleship")

        self.player_ships_to_place = self.SHIP_LENGTHS.copy()
        self.computer_ships = self.SHIP_LENGTHS.copy()
        self.player_ships_placed = {} # (row, col): ship_name
        self.computer_ships_placed = {} # (row, col): ship_name

        self.player_hits = set()
        self.player_misses = set()
        self.computer_hits = set()
        self.computer_misses = set()
        self.computer_guesses = set()

        self.current_ship_to_place = None
        self.current_orientation = "h" # 'h' or 'v'
        self.state = "PLACING_SHIPS" # PLACING_SHIPS, PLAYER_TURN, COMPUTER_TURN, GAME_OVER

        # --- UI Elements ---
        # Player Board Frame
        player_outer_frame = tk.Frame(self.window, borderwidth=2, relief=tk.GROOVE)
        player_outer_frame.grid(row=0, column=0, padx=5, pady=5)
        tk.Label(player_outer_frame, text="Your Board").grid(row=0, column=0, columnspan=self.GRID_SIZE + 1)
        self.player_frame = tk.Frame(player_outer_frame)
        self.player_frame.grid(row=1, column=0)
        self.player_buttons = self._create_grid(self.player_frame, self.player_board_click, self.PLAYER_BOARD_BG)
        self._add_grid_labels(player_outer_frame, 1, 0)

        # Computer Board Frame
        computer_outer_frame = tk.Frame(self.window, borderwidth=2, relief=tk.GROOVE)
        computer_outer_frame.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(computer_outer_frame, text="Computer's Board").grid(row=0, column=0, columnspan=self.GRID_SIZE + 1)
        self.computer_frame = tk.Frame(computer_outer_frame)
        self.computer_frame.grid(row=1, column=0)
        self.computer_buttons = self._create_grid(self.computer_frame, self.computer_board_click, self.COMPUTER_BOARD_BG)
        self._add_grid_labels(computer_outer_frame, 1, 0)

        # Controls Frame
        controls_frame = tk.Frame(self.window)
        controls_frame.grid(row=1, column=0, columnspan=2, pady=10)

        # Ship Selection
        ship_select_frame = tk.LabelFrame(controls_frame, text="Place Your Ships")
        ship_select_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ns")
        self.ship_buttons = {}
        row_num = 0
        for ship, length in self.SHIP_LENGTHS.items():
            btn = tk.Button(ship_select_frame, text=f"{ship} ({length})",
                            command=lambda s=ship: self.select_ship(s))
            btn.grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)
            self.ship_buttons[ship] = btn
            row_num += 1

        self.orientation_button = tk.Button(ship_select_frame, text="Orientation: H", command=self.toggle_orientation)
        self.orientation_button.grid(row=row_num, column=0, sticky="ew", padx=5, pady=2)

        self.start_button = tk.Button(ship_select_frame, text="Start Game", command=self.start_game, state="disabled")
        self.start_button.grid(row=row_num + 1, column=0, sticky="ew", padx=5, pady=5)

        # Log and Legend
        log_legend_frame = tk.Frame(controls_frame)
        log_legend_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ns")

        self.log = tk.Text(log_legend_frame, width=40, height=10, state="disabled")
        self.log.pack(pady=5)

        self.legend = tk.Label(log_legend_frame, justify=tk.LEFT, text=
            f" Legends:\n"
            f" Your Ship: {self.PLACED_SHIP_COLOR}\n"
            f" Your Hit: {self.HIT_COLOR_COMPUTER}\n"
            f" Your Miss: {self.MISS_COLOR_COMPUTER}\n"
            f" Opponent Hit: {self.HIT_COLOR_PLAYER}\n"
            f" Opponent Miss: {self.MISS_COLOR_PLAYER}"
        )
        self.legend.pack()

        self.log_message("Place your ships. Select a ship type, orientation, then click the starting cell on 'Your Board'.")
        self.window.mainloop()

    def _create_grid(self, parent_frame, click_handler, bg_color):
        buttons = []
        for r in range(self.GRID_SIZE):
            row_buttons = []
            for c in range(self.GRID_SIZE):
                button = tk.Button(parent_frame, text="", width=2, height=1, bg=bg_color,
                                   command=lambda row=r, col=c: click_handler(row, col))
                button.grid(row=r, column=c)
                row_buttons.append(button)
            buttons.append(row_buttons)
        return buttons

    def _add_grid_labels(self, parent_frame, start_row, start_col):
        # Add column labels (A-J) below the grid
        for i in range(self.GRID_SIZE):
            label = tk.Label(parent_frame, text=chr(65 + i))
            label.grid(row=start_row + self.GRID_SIZE, column=start_col + i)
        # Add row labels (1-10) to the right of the grid
        for i in range(self.GRID_SIZE):
            label = tk.Label(parent_frame, text=str(i + 1))
            label.grid(row=start_row + i, column=start_col + self.GRID_SIZE)

    def log_message(self, message):
        self.log.config(state="normal")
        self.log.insert("1.0", message + "\n")
        self.log.config(state="disabled")

    def select_ship(self, ship_name):
        if self.state == "PLACING_SHIPS":
            if ship_name in self.player_ships_to_place:
                self.current_ship_to_place = ship_name
                self.log_message(f"Selected {ship_name}. Orientation: {self.current_orientation.upper()}. Click the top/left cell.")
            else:
                self.log_message(f"{ship_name} already placed.")

    def toggle_orientation(self):
        if self.state == "PLACING_SHIPS":
            self.current_orientation = "v" if self.current_orientation == "h" else "h"
            self.orientation_button.config(text=f"Orientation: {self.current_orientation.upper()}")
            if self.current_ship_to_place:
                 self.log_message(f"Changed orientation to {self.current_orientation.upper()}. Click the top/left cell for {self.current_ship_to_place}.")

    def player_board_click(self, row, col):
        if self.state == "PLACING_SHIPS" and self.current_ship_to_place:
            self.place_player_ship(row, col)
        elif self.state == "PLAYER_TURN" or self.state == "COMPUTER_TURN":
            self.log_message("Click on the Computer's board to attack.")
        elif self.state == "GAME_OVER":
             self.log_message("Game is over.")
        else:
             self.log_message("Select a ship type first.")

    def get_ship_cells(self, row, col, length, orientation):
        cells = []
        if orientation == "h":
            if col + length <= self.GRID_SIZE:
                for i in range(length):
                    cells.append((row, col + i))
        elif orientation == "v":
            if row + length <= self.GRID_SIZE:
                for i in range(length):
                    cells.append((row + i, col))
        return cells

    def get_neighbors(self, cell, include_diagonals=True):
        r, c = cell
        neighbors = []
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                if not include_diagonals and abs(dr) + abs(dc) != 1:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.GRID_SIZE and 0 <= nc < self.GRID_SIZE:
                    neighbors.append((nr, nc))
        return neighbors

    def is_placement_valid(self, cells_to_place):
        if not cells_to_place: # Check if cells are within bounds (handled by get_ship_cells)
             return False, "Ship placement is out of bounds."

        all_placement_cells_and_neighbors = set(cells_to_place)
        for cell in cells_to_place:
            all_placement_cells_and_neighbors.update(self.get_neighbors(cell))

        for existing_cell, ship_name in self.player_ships_placed.items():
             if existing_cell in all_placement_cells_and_neighbors:
                 return False, "Ship placement overlaps or is adjacent to another ship."

        return True, ""

    def place_player_ship(self, row, col):
        ship_name = self.current_ship_to_place
        length = self.SHIP_LENGTHS[ship_name]
        orientation = self.current_orientation

        ship_cells = self.get_ship_cells(row, col, length, orientation)

        is_valid, message = self.is_placement_valid(ship_cells)

        if is_valid:
            for r, c in ship_cells:
                self.player_ships_placed[(r, c)] = ship_name
                self.player_buttons[r][c].config(bg=self.PLACED_SHIP_COLOR, state="disabled")

            self.log_message(f"Placed {ship_name}.")
            self.ship_buttons[ship_name].config(state="disabled")
            del self.player_ships_to_place[ship_name]
            self.current_ship_to_place = None

            if not self.player_ships_to_place:
                self.log_message("All ships placed. Press 'Start Game'.")
                self.start_button.config(state="normal")
                self.orientation_button.config(state="disabled")
        else:
            self.log_message(f"Invalid placement for {ship_name}: {message}")


    def start_game(self):
        if not self.player_ships_to_place and self.state == "PLACING_SHIPS":
            self.state = "PLAYER_TURN"
            self.start_button.config(state="disabled")
            self.orientation_button.config(state="disabled")
            for btn in self.ship_buttons.values():
                btn.config(state="disabled")

            self.place_computer_ships()
            self.log_message("Game started! Your turn to attack.")
        elif self.state != "PLACING_SHIPS":
             self.log_message("Game already started.")
        else:
            self.log_message("Please place all your ships first.")

    def place_computer_ships(self):
        self.computer_ships_placed = {}
        for ship, length in self.computer_ships.items():
            placed = False
            attempts = 0
            while not placed and attempts < 200: # Limit attempts to prevent infinite loop
                attempts += 1
                orientation = choice(["h", "v"])
                if orientation == "h":
                    row = randint(0, self.GRID_SIZE - 1)
                    col = randint(0, self.GRID_SIZE - length)
                else: # orientation == "v"
                    row = randint(0, self.GRID_SIZE - length)
                    col = randint(0, self.GRID_SIZE - 1)

                ship_cells = self.get_ship_cells(row, col, length, orientation)
                is_valid, _ = self._is_computer_placement_valid(ship_cells)

                if is_valid:
                    for r, c in ship_cells:
                        self.computer_ships_placed[(r, c)] = ship
                    placed = True
            if not placed:
                 # This should ideally not happen with enough space, but handle defensively
                 print(f"Error: Could not place computer ship {ship}. Check placement logic/grid size.")
                 # Consider alternative strategies or error handling here
        print("Computer ships placed (hidden):", self.computer_ships_placed) # Debugging line

    def _is_computer_placement_valid(self, cells_to_place):
        # Simplified validation for computer, reusing logic but on computer's ships
        if not cells_to_place:
             return False, "Out of bounds"

        all_placement_cells_and_neighbors = set(cells_to_place)
        for cell in cells_to_place:
            all_placement_cells_and_neighbors.update(self.get_neighbors(cell))

        for existing_cell in self.computer_ships_placed.keys():
             if existing_cell in all_placement_cells_and_neighbors:
                 return False, "Overlap or adjacent"

        return True, ""


    def computer_board_click(self, row, col):
        if self.state != "PLAYER_TURN":
            self.log_message("Not your turn or game not started/over.")
            return

        target_cell = (row, col)
        button = self.computer_buttons[row][col]

        if target_cell in self.player_hits or target_cell in self.player_misses:
            self.log_message("You already attacked this cell.")
            return

        if target_cell in self.computer_ships_placed:
            ship_hit = self.computer_ships_placed[target_cell]
            self.player_hits.add(target_cell)
            button.config(bg=self.HIT_COLOR_COMPUTER, text="X", state="disabled")
            self.log_message(f"Hit computer's {ship_hit}!")
            if self.check_sunk(ship_hit, self.computer_ships_placed, self.player_hits):
                self.log_message(f"*** You sunk the computer's {ship_hit}! ***")
                if self.check_game_over(): return # Check game over immediately
            # Player gets another turn after a hit? No, standard rules turn passes.
            self.state = "COMPUTER_TURN"
            self.window.after(500, self.computer_turn) # Give player time to see result
        else:
            self.player_misses.add(target_cell)
            button.config(bg=self.MISS_COLOR_COMPUTER, text="o", state="disabled")
            self.log_message("Miss!")
            self.state = "COMPUTER_TURN"
            self.window.after(500, self.computer_turn)

    def computer_turn(self):
        if self.state != "COMPUTER_TURN":
            return # Should not happen if logic is correct

        self.log_message("Computer's turn...")
        # Simple random guessing AI
        while True:
            row = randint(0, self.GRID_SIZE - 1)
            col = randint(0, self.GRID_SIZE - 1)
            target_cell = (row, col)
            if target_cell not in self.computer_guesses:
                self.computer_guesses.add(target_cell)
                break

        button = self.player_buttons[row][col]

        if target_cell in self.player_ships_placed:
            ship_hit = self.player_ships_placed[target_cell]
            self.computer_hits.add(target_cell)
            # Change color of player's ship on player's board
            button.config(bg=self.HIT_COLOR_PLAYER) # No text change needed? Or 'X'?
            self.log_message(f"Computer hit your {ship_hit} at {chr(65+col)}{row+1}!")
            if self.check_sunk(ship_hit, self.player_ships_placed, self.computer_hits):
                self.log_message(f"*** Computer sunk your {ship_hit}! ***")
                if self.check_game_over(): return
            # Computer gets another turn after hit? No.
            self.state = "PLAYER_TURN"
            self.log_message("Your turn.")
        else:
            self.computer_misses.add(target_cell)
            # Mark miss on player's board
            if button['bg'] == self.PLAYER_BOARD_BG: # Don't overwrite ship color if already placed
                button.config(bg=self.MISS_COLOR_PLAYER)
            self.log_message(f"Computer missed at {chr(65+col)}{row+1}.")
            self.state = "PLAYER_TURN"
            self.log_message("Your turn.")


    def check_sunk(self, ship_name, ships_placed_dict, hits_set):
        ship_cells = {pos for pos, name in ships_placed_dict.items() if name == ship_name}
        return ship_cells.issubset(hits_set)

    def check_game_over(self):
        player_ships_remaining = set(self.player_ships_placed.values())
        computer_ships_remaining = set(self.computer_ships_placed.values())

        player_all_sunk = True
        for ship in player_ships_remaining:
            if not self.check_sunk(ship, self.player_ships_placed, self.computer_hits):
                player_all_sunk = False
                break

        computer_all_sunk = True
        for ship in computer_ships_remaining:
            if not self.check_sunk(ship, self.computer_ships_placed, self.player_hits):
                computer_all_sunk = False
                break

        if player_all_sunk:
            self.log_message("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.log_message("Game Over! Computer wins!")
            self.log_message("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.state = "GAME_OVER"
            self._disable_boards()
            return True
        elif computer_all_sunk:
            self.log_message("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.log_message("Game Over! You win!")
            self.log_message("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.state = "GAME_OVER"
            self._disable_boards()
            return True
        return False

    def _disable_boards(self):
         for r in range(self.GRID_SIZE):
              for c in range(self.GRID_SIZE):
                   self.player_buttons[r][c].config(state="disabled")
                   self.computer_buttons[r][c].config(state="disabled")


Battleship()