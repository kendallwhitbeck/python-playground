import multiprocessing
# Add this near the top

# Need a top-level function for multiprocessing to pickle
def evaluate_single_pair(args):
    """Worker function for parallel evaluation."""
    genome_tarnished, genome_margit, config_tarnished, config_margit, gen_num, pop_idx, trainer_name, save_states_flag = args

    # CRITICAL: Re-initialize necessary components within the worker process if needed.
    # Pygame display and event handling MUST NOT be initialized or used here
    # if the main process is also using it. Stick to headless.

    # Create networks within the worker
    try:
        player_net = neat.nn.FeedForwardNetwork.create(genome_tarnished, config_tarnished)
        enemy_net = neat.nn.FeedForwardNetwork.create(genome_margit, config_margit)
    except Exception as e:
        print(f"Error creating network in worker for pop {pop_idx}: {e}")
        # Handle error appropriately, maybe return default low fitness
        return genome_tarnished.key, genome_margit.key, -10000, -10000 # Return keys and fitness

    # *** IMPORTANT: Modifications needed in play_game ***
    # 1. Ensure play_game(..., headless=True) DOES NOT use pygame.display, pygame.event, etc.
    # 2. Pass necessary info (gen_num, pop_idx, trainer_name, save_states_flag) into play_game
    #    if it needs them for logging or conditional saving within the headless run.
    #    (Alternatively, return more data from play_game and handle saving in the main process).

    # Assuming play_game is modified to accept these and run headlessly:
    player_fitness, enemy_fitness = play_game(
        player_net,
        enemy_net,
        headless=True,
        # Pass other args if needed by the modified play_game for logging/saving:
        # generation=gen_num,
        # population_index=pop_idx,
        # current_trainer=trainer_name,
        # save_game_state=save_states_flag
    )

    # Return the keys along with fitness for proper assignment later
    return genome_tarnished.key, genome_margit.key, player_fitness, enemy_fitness

# Modify eval_genomes
def eval_genomes(genomes_tarnished, genomes_margit, config_tarnished, config_margit):
    global curr_gen
    global curr_pop
    curr_pop = 0 # Reset population counter for this generation
    curr_gen += 1
    print(f"Starting evaluation for Generation {curr_gen} (Trainer: {curr_trainer})")

    # Ensure game state directory exists (might be created by workers if saving there)
    # pathlib.Path(f"{GAMESTATES_PATH}/gen_{curr_gen}").mkdir(parents=True, exist_ok=True)

    if type(genomes_tarnished) == dict:
        genomes_tarnished_dict = genomes_tarnished
        genomes_tarnished_list = list(genomes_tarnished.items())
    else: # Assume list of tuples
        genomes_tarnished_list = genomes_tarnished
        genomes_tarnished_dict = dict(genomes_tarnished)

    if type(genomes_margit) == dict:
        genomes_margit_dict = genomes_margit
        genomes_margit_list = list(genomes_margit.items())
    else: # Assume list of tuples
        genomes_margit_list = genomes_margit
        genomes_margit_dict = dict(genomes_margit)

    # Prepare arguments for parallel processing
    tasks = []
    num_pairs = min(len(genomes_tarnished_list), len(genomes_margit_list))
    for i in range(num_pairs):
        genome_id_player, genome_tarnished = genomes_tarnished_list[i]
        genome_id_enemy, genome_margit = genomes_margit_list[i]

        # Initialize fitness to a default (or 0) before evaluation
        genome_tarnished.fitness = 0
        genome_margit.fitness = 0

        # Add task arguments
        # Determine if this specific game state should be saved
        should_save = SAVE_GAMESTATES # Base decision on global setting
        # You could add more logic here, e.g., only save top N% based on previous gen?

        tasks.append((
            genome_tarnished, genome_margit,
            config_tarnished, config_margit,
            curr_gen, i + 1, # Pass generation and population index
            curr_trainer, # Pass current trainer being evaluated
            should_save
        ))

    # --- Parallel Execution ---
    # Use context manager for proper pool cleanup
    # Set processes=N to control core usage, None uses cpu_count()
    num_workers = multiprocessing.cpu_count() - 1 # Leave one core for OS/main process
    print(f"Using {num_workers} worker processes...")
    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(evaluate_single_pair, tasks)

    # --- Process Results ---
    print("Evaluation complete. Assigning fitness...")
    for result in results:
        tarnished_key, margit_key, tarnished_fitness, margit_fitness = result

        # Assign fitness back to the correct genomes using the dictionaries
        if tarnished_key in genomes_tarnished_dict:
             genomes_tarnished_dict[tarnished_key].fitness = tarnished_fitness
        else:
             print(f"Warning: Tarnished key {tarnished_key} not found in dict after evaluation.")

        if margit_key in genomes_margit_dict:
            genomes_margit_dict[margit_key].fitness = margit_fitness
        else:
            print(f"Warning: Margit key {margit_key} not found in dict after evaluation.")

        # Ensure fitness is not None (check for errors during evaluation)
        # assert genomes_tarnished_dict[tarnished_key].fitness is not None
        # assert genomes_margit_dict[margit_key].fitness is not None
    print(f"Fitness assignment complete for Generation {curr_gen}")
