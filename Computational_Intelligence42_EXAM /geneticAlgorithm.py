import logging
from collections import namedtuple
import random
from copy import deepcopy
import quarto
import math
import numpy as np
import itertools

Individual = namedtuple("Individual", ["genome", "fitness"])
# Genome -> array of 8 elements (4 figures + 4 positions)

BOARD_SIZE = 4
GENOME_SIZE = BOARD_SIZE * 2
POPULATION_SIZE = 512
NUM_GENERATIONS = 40
OFFSPRING_SIZE = 100
TOURNAMENT_SIZE = 5
CROSSOVER_THRESHOLD = 0.4
MUTATION_THRESHOLD = 0.1

SELF_CHOOSE = 0
SELF_PLACE = 1


class GeneticAlgorithm():
    def __init__(self, current_game: quarto.Quarto):
        self.current_game = current_game
        self.iterations = 4
    
    def tupleToIndex(self, x, y):
        return 4 * y + x

    def indexToTuple(self, index):
        x = index % BOARD_SIZE
        y = math.floor(index / BOARD_SIZE)
        return (x,y)

    def try_place(self, x: int, y: int) -> bool:
        '''
        Verify if a piece is placeable but don't actually place it 
        '''
        return not (y < 0 or x < 0 or x > 3 or y > 3 or self.current_game._board[y, x] >= 0)

    def place(self, x: int, y: int, piece_index: int) -> bool:
        '''
        Place piece in coordinates (x, y). Returns true on success
        '''
        if self.try_place(x, y):
            self.current_game._board[y, x] = piece_index
            self.current_game._binary_board[y, x][:] = self.current_game._Quarto__pieces[piece_index].binary
            return True
        return False

    def unplace(self, x: int, y: int) -> bool:
        '''
        Take away piece in coordinates (x, y). Returns true on success
        '''
        self.current_game._board[y, x] = -1
        self.current_game._binary_board[y, x][:] = np.nan
        return True
    
    def available_positions(self, genome: list = None):
        '''
        Lists available positions on the board, considering also the positions potentially taken by the genome
        '''
        listAvailablePositions = []

        for x in range(self.current_game.BOARD_SIDE):
            for y in range(self.current_game.BOARD_SIDE):
                if self.try_place(x, y):
                    coord = self.tupleToIndex(x, y)
                    listAvailablePositions.append(coord)
        #print(listAvailablePositions)

        if genome is not None:
            for i in range(GENOME_SIZE//2, GENOME_SIZE//2 + self.iterations):
                if (genome[i] in listAvailablePositions) and len(listAvailablePositions) > 0:
                    listAvailablePositions.remove(genome[i])
        
        return listAvailablePositions
    
    
    def available_pieces(self, genome: list = None):
        '''
        Lists available pieces, considering also the pieces potentially taken by the genome
        '''
        listAvailablePieces = list(range(16))
        
        if genome is not None:
            for i in range(0, self.iterations):
                if (genome[i] in listAvailablePieces):
                    listAvailablePieces.remove(genome[i])

        for x in range(self.current_game.BOARD_SIDE):
            for y in range(self.current_game.BOARD_SIDE):
                current_piece = self.current_game._board[y,x]
                if current_piece != -1 and current_piece in listAvailablePieces:
                    listAvailablePieces.remove(current_piece)   
                    
        return listAvailablePieces
    
    
    def tournament(self, population, tournament_size=TOURNAMENT_SIZE):        
        '''
        Parent selection - TOURNAMENT version
        '''  
        return max(random.choices(population, k=tournament_size), key=lambda i: i.fitness) 

    def roulette_wheel_selection(self, population):
        '''
        Parent selection - ROULETTE WHEEL version
        '''
        fitness_sum = sum(individual.fitness for individual in population)
        if fitness_sum == 0:
            return self.tournament(population, TOURNAMENT_SIZE)

        normalized_fitness = [individual.fitness/fitness_sum for individual in population]
        
        cumulative_probabilities = [sum(normalized_fitness[:i+1]) for i in range(len(normalized_fitness))]
        random_num = random.random()
        for i, prob in enumerate(cumulative_probabilities):
            if random_num <= prob:
                return population[i]

    def cross_over_1(self, genome_1: list, genome_2: list):
        '''
        Crossover between genomes. The new genome will have some genes from first parent, and other genes from second one.
        '''
        new_genome = [-1]*GENOME_SIZE

        for i in range(0, self.iterations):
            if (random.randint(0,1) > CROSSOVER_THRESHOLD):
                new_genome[i] = genome_1[i]
            else:
                new_genome[i] = genome_2[i]

        for i in range(GENOME_SIZE//2, GENOME_SIZE//2 + self.iterations):
            if (random.randint(0,1) > CROSSOVER_THRESHOLD):
                new_genome[i] = genome_1[i]
            else:
                new_genome[i] = genome_2[i]

        return new_genome
    
    def cross_over_2(self, genome_1, genome_2):
        piece_changes, pos_exchanges = random.randint(1, 3), random.randint(1, 4)
        new_genome = deepcopy(genome_1)

        for i in range(1, piece_changes):
            new_genome[i] = genome_2[i]
        for i in range(piece_changes, 4 - piece_changes):
            new_genome[i] = genome_2[i]
        
        for i in range(1, pos_exchanges):
            new_genome[4 + i] = genome_2[4 + i]
        for i in range(pos_exchanges, 4 - pos_exchanges):
            new_genome[4 + i] = genome_2[4 + i]

        return new_genome

    
    def mutation_1(self, genome): 
        """
        In the genome, "pieces" genes are swapped among each other, 
        and "position" genes are swapped among each other too.
        """
        new_genome = deepcopy(genome)

        if (random.randint(0,1) > MUTATION_THRESHOLD): # mutate pieces
            i_1, i_2 = random.sample(range(self.iterations), 2)
            new_genome[i_1], new_genome[i_2] = new_genome[i_2], new_genome[i_1]
        
        if (random.randint(0,1) > MUTATION_THRESHOLD): # mutate positions
            i_1, i_2 = random.sample(range(GENOME_SIZE//2, GENOME_SIZE//2 + self.iterations), 2)
            new_genome[i_1], new_genome[i_2] = new_genome[i_2], new_genome[i_1]
        
        return new_genome  

    def mutation_2(self, genome: list): 
        new_genome = deepcopy(genome)

        for pieceIndex in range(1, self.iterations): # mutate pieces
            if (random.randint(0,1) > MUTATION_THRESHOLD):
                available_pieces = self.available_pieces(new_genome)
                if (len(available_pieces) > 0):
                    new_genome[pieceIndex] = (random.choice(available_pieces))

        for posIndex in range(GENOME_SIZE//2, GENOME_SIZE//2 + self.iterations): # mutate positions
            if (random.randint(0,1) > MUTATION_THRESHOLD):
                available_positions = self.available_positions(new_genome)
                if (len(available_positions) > 0):
                    new_genome[posIndex] = (random.choice(available_positions))
        return new_genome

    def isWinning(self, current_piece: int, pos_index: int):
        pos_tuple = self.indexToTuple(pos_index)
        is_winning = False
        
        if (self.place(pos_tuple[0], pos_tuple[1], current_piece)):
            is_winning = True if (self.current_game.check_winner() >= 0) else False
            self.unplace(pos_tuple[0], pos_tuple[1])

        return is_winning

    def isWinnable(self, current_piece: int):
        available_positions = self.available_positions()
        for pos in available_positions:
            if self.isWinning(current_piece, pos):
                return True
        return False

    def computeFitness (self,genome: list, strategyType: int):
        tot_reward = 0
 
        for i in range(self.iterations):
            piece = genome[i]
            pos_index = genome[GENOME_SIZE//2 + i]
            

            winning_move = self.isWinning(piece, pos_index)
            is_winnable = self.isWinnable(piece)

            # My turn
            if i == 0:
                if strategyType == SELF_PLACE:
                    # Opponent chose a piece, and I need to place it now
                    if (winning_move):  
                        # am I predicting winning move?
                        tot_reward = 1
                        break
                    if (is_winnable):   
                        # is the opponent dumb enough to give me a potentially winning piece?
                        tot_reward += 0.5
                        break
                elif strategyType == SELF_CHOOSE:
                    # I need to choose a piece for the opponent
                    # therefore, the first genome does not make sense
                    continue

            # Opponent turn
            elif i == 1:
                if strategyType == SELF_CHOOSE:
                    # I choose a piece for the opponent
                    if (winning_move):
                        # can the opponent make a winning move with this?
                        tot_reward = -1
                        break
                    if (is_winnable):
                        # am I being dumb enough to give the opponent a potentially winning piece?
                        tot_reward -= 0.5
                        break
                    else:
                        # the opponent cannot do anything with this piece!
                        tot_reward += 0.25
                if strategyType == SELF_PLACE:
                    # For now this move does not make sense, 
                    # as I will be re-executing the algorithm later on!
                    continue
               
            # Trying to look ahead
            elif i == 2 and (winning_move or is_winnable):
                tot_reward += 0.25
            elif i == 3 and (winning_move or is_winnable):
                tot_reward -= 0.25
            
            
        return tot_reward

    def initPopulation(self, strategyType: int, size: int = POPULATION_SIZE):
        '''
        Generate initial population. StrategyType is needed to evaluate fitness.
        '''
        population = []

        remaining = len(self.available_pieces())
        self.iterations = min(remaining, self.iterations)

        for p in range(size):
            genome = [-1]*GENOME_SIZE
                
            if self.current_game._Quarto__selected_piece_index == -1:
                genome[0] = random.randint(0,15)
            else:
                genome[0] = self.current_game._Quarto__selected_piece_index
                
            for i in range(1,self.iterations):
                listAvailablePieces = self.available_pieces(genome)
                genome[i] = random.choice(listAvailablePieces)

            for i in range(GENOME_SIZE//2, GENOME_SIZE//2 + self.iterations):
                listAvailablePositions = self.available_positions(genome)
                genome[i] = random.choice(listAvailablePositions)
                
            population.append(Individual(genome, self.computeFitness(genome, strategyType)))
        
        return population


    def my_move(self, strategyType: int):
        population = self.initPopulation(strategyType)
        if (self.iterations == 1):
            return (population[0][0][1], population[0][0][4])

        for g in range(NUM_GENERATIONS):
            
            offspring = list()
            for i in range(OFFSPRING_SIZE):
                if random.random() > MUTATION_THRESHOLD:
                    # mutation                       
                    p = self.roulette_wheel_selection(population)   
                    o = self.mutation_2(p.genome)

                    f = self.computeFitness(o, strategyType)

                    if (f > p.fitness):
                        offspring.append(Individual(o, f)) 
                    else:
                        offspring.append(p) 

                if random.random() > CROSSOVER_THRESHOLD: 
                    # crossover                                        
                    p1 = self.roulette_wheel_selection(population)                 
                    p2 = self.roulette_wheel_selection(population)

                    o = self.cross_over_1(p1.genome, p2.genome)            
                    f = self.computeFitness(o, strategyType)

                    offspring.append(Individual(o,f))

            # append offspring to population                                   
            population += offspring

            # code to have unique elements in population
            # given that we use "namedtuple" types we need to do it manually
            unique_population = []
            unique_genomes = []
            for individual in population:
                if individual.genome not in unique_genomes:
                    unique_genomes.append(individual.genome)
                    unique_population.append(individual)

            # take most promising genomes only, according to fitness
            population = sorted(unique_population, key=lambda i: i[1], reverse = True)[:POPULATION_SIZE]
            #print(*population, sep="\n")

            best_fitness = population[0].fitness
            # sometimes the algoithm gets stuck in finding only losing solutions.
            # by reinitializing the population, we introduce randomness again
            # almost always, the algorithm gets back up
            if best_fitness < 0:
                print("yeuch")
                population += self.initPopulation(strategyType, POPULATION_SIZE * 2)
            population = sorted(unique_population, key=lambda i: i[1], reverse = True)[:POPULATION_SIZE]
        
        best_genome = population[0].genome

        #print(population[0])
        piece_to_give = best_genome[1]
        position_to_play = self.indexToTuple(best_genome[4])
        #print((piece_to_give, position_to_play))
        return (piece_to_give, position_to_play)

class GeneticPlayer(quarto.Player):
    """GA player"""

    def __init__(self, current_game: quarto.Quarto):
        #super().__init__(quarto)
        self.geneticAlgorithm = GeneticAlgorithm(current_game)

        self.piece_to_give = None
        self.pos_chosen = None

    def choose_piece(self):
        (self.piece_to_give, self.pos_chosen) = self.geneticAlgorithm.my_move(SELF_CHOOSE)
        #print("GA chooses piece - ", self.piece_to_give)
        return self.piece_to_give

    def place_piece(self):
        (self.piece_to_give, self.pos_chosen) = self.geneticAlgorithm.my_move(SELF_PLACE)
        #print("GA chooses pos - ", self.pos_chosen)
        return self.pos_chosen

