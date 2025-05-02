# In settings.py or main.py
TRAINING_MODE = True # Set this to True when running main(), False for replays

# Modify draw()
def draw(headless=False):
    if headless:
        return # Don't do anything if in headless mode

    WIN.blit(BG, (0,0))
    # ... rest of your drawing code ...
    pygame.display.update()

# Modify play_game()
def play_game(tarnished_net, margit_net, headless=False) -> tuple[int]:
    # ... (initial setup) ...

    clock = pygame.time.Clock()
    updates = 0
    try:
        running = True
        while running:
            # Limit clock only if not headless, or use a different limit?
            # If headless, the simulation can run as fast as the CPU allows.
            # You might not even need the clock tick IF MAX_UPDATES_PER_GAME
            # is the primary termination condition. Test this.
            if not headless:
                 clock.tick(TPS) # Or maybe a lower TPS if visualization isn't needed?

            # Event handling is only needed if visualizing or interacting
            if not headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        # Potentially raise an exception or handle differently in headless
                        # to signal intentional stop? Or rely on MAX_UPDATES.

            # ... (get current state) ...
            # ... (get actions) ...
            # ... (do actions) ...
            # ... (update entities) ...

            # **** CRITICAL CHANGE ****
            if not headless:
                draw(headless=False) # Only draw if not headless

            # ... (append game state - consider if this is needed when headless) ...
            # If you ONLY need the final state for fitness, you could optimize
            # by not storing every single state tick during headless evaluation.
            # However, your current fitness likely relies on the full history.

            updates += 1
            if updates > MAX_UPDATES_PER_GAME:
                game_result["notes"] = "Game stalemated"
                running = False
    # ... (exception handling) ...
    finally:
        # ... (calculate fitness) ...

        # **** Consider conditional saving ****
        # Do you NEED to save game states during normal training runs?
        # Only save if SAVE_GAMESTATES is True OR if not headless?
        # Saving JSON for every game is I/O intensive.
        if SAVE_GAMESTATES or not headless:
            file_name = str(curr_pop) + f"_{curr_trainer}"
            # ... (rest of file saving) ...

    return game_result[f"{trainer_str(Entities.TARNISHED)}_fitness"], game_result[f"{trainer_str(Entities.MARGIT)}_fitness"]


# Modify eval_genomes to pass the headless flag
def eval_genomes(genomes_tarnished, genomes_margit, config_tarnished, config_margit):
    global curr_gen
    global curr_pop
    # ... (setup) ...

    for (genome_id_player, genome_tarnished), (genome_id_enemy, genome_margit) in zip(genomes_tarnished, genomes_margit):
        # ... (create networks) ...

        # **** PASS HEADLESS FLAG ****
        # Use TRAINING_MODE from settings or pass directly
        is_headless = not replays # Assumes replays=False means training
        player_fitness, enemy_fitness = play_game(player_net, enemy_net, headless=is_headless)

        # ... (assign fitness) ...

# Make sure when you run replays, TRAINING_MODE is False or you handle the headless flag appropriately
# In process_replays or replay_game:
def replay_game(game_data: dict):
    # ... setup ...
    for frame in game_data["game_states"]:
        # ... clock tick ...
        # ... event handling ...
        # ... update entities from frame ...

        # **** Ensure drawing happens during replay ****
        draw_replay(game_data) # Your replay draw function handles its own drawing


    # You might need to adjust draw_replay if it relies on the main draw() function.
    # Ensure it forces drawing even if a global headless flag is set.
