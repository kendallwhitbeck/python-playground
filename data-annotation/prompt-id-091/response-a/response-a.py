import multiprocessing

def play_game_parallel(args):
    # Extract arguments
    tarnished_net, margit_net, generation, population_id, trainer = args
    
    # Create fresh entities for this process
    tarnished = Tarnished()
    margit = Margit()
    tarnished.give_target(margit)
    margit.give_target(tarnished)
    
    # Simplified game result structure
    game_result = {
        "winner": "draw",
        f"{trainer_str(Entities.TARNISHED)}_fitness": 0,
        f"{trainer_str(Entities.MARGIT)}_fitness": 0,
        "game_version": GAME_VERSION,
        "fitness_version": FITNESS_VERSION,
        "trainer": trainer,
        "generation": generation,
        "population": population_id,
        "game_states": [],  # Only keep if needed for fitness
    }
    
    updates = 0
    try:
        # Main game loop without visualization
        while updates < MAX_UPDATES_PER_GAME:
            # Get current state
            curr_state = {
                "tick": updates,
                "tarnished": {"state": tarnished.get_state()},
                "margit": {"state": margit.get_state()}
            }
            
            # Get and apply actions
            tarnish_actions = get_tarnished_actions(tarnished_net, curr_state)
            margit_actions = get_margit_actions(margit_net, curr_state)
            
            tarnished.do_actions(tarnish_actions)
            margit.do_actions(margit_actions)
            
            # Update game state
            tarnished.update()
            margit.update()
            
            # Only save states if absolutely necessary for fitness calculation
            if SAVE_MINIMAL_STATES:
                game_result["game_states"].append(curr_state)
            
            updates += 1
            
    except TarnishedDied:
        game_result["winner"] = "margit"
    except MargitDied as e:
        game_result["winner"] = "tarnished"
    finally:
        # Calculate fitness
        tarnished_fitness, _ = get_tarnished_fitness(game_result)
        margit_fitness, _ = get_margit_fitness(game_result)
        
        # Optionally save game result to file (consider making this optional)
        if SAVE_GAMESTATES:
            filename = f"{GAMESTATES_PATH}/gen_{generation}/{population_id}_{trainer}.json"
            with open(filename, 'w') as f:
                json.dump(game_result, f)
    
    return tarnished_fitness, margit_fitness

def eval_genomes(genomes_tarnished, genomes_margit, config_tarnished, config_margit):
    global curr_gen
    global curr_pop
    curr_gen += 1
    pathlib.Path(f"{GAMESTATES_PATH}/gen_{curr_gen}").mkdir(parents=True, exist_ok=True)

    # Convert to lists if they're dictionaries
    if type(genomes_tarnished) == dict:
        genomes_tarnished = list(genomes_tarnished.items())
    if type(genomes_margit) == dict:
        genomes_margit = list(genomes_margit.items())

    # Initialize fitness
    for _, genome in genomes_tarnished:
        genome.fitness = 0
    for _, genome in genomes_margit:
        genome.fitness = 0

    # Prepare arguments for parallel processing
    args_list = []
    for idx, ((_, genome_tarnished), (_, genome_margit)) in enumerate(zip(genomes_tarnished, genomes_margit)):
        player_net = neat.nn.FeedForwardNetwork.create(genome_tarnished, config_tarnished)
        enemy_net = neat.nn.FeedForwardNetwork.create(genome_margit, config_margit)
        args_list.append((player_net, enemy_net, curr_gen, idx, curr_trainer))
    
    # Use multiprocessing to evaluate genomes in parallel
    with multiprocessing.Pool() as pool:
        results = pool.map(play_game_parallel, args_list)

    # Assign fitness values back to genomes
    for idx, (tarnished_fitness, margit_fitness) in enumerate(results):
        genomes_tarnished[idx][1].fitness = tarnished_fitness
        genomes_margit[idx][1].fitness = margit_fitness

