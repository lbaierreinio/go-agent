# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
from copy import deepcopy
from collections import deque
import time 
import random
import math 


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.root = None
        self.autoplay = True

    def compare(self, board_one, board_two):
        length = len(board_one)
        for i in range(0,length):
            for j in range(0,length):
                for k in range(0,4):
                    if (board_one[i][j][k] != board_two[i][j][k]):
                        return False

        return True
                
    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        # if no root instantiated yet 

        if (self.root == None):
            self.root = MCTSNode(None, deepcopy(my_pos), deepcopy(adv_pos), max_step, deepcopy(chess_board), None, True)
            self.root.time_limit = 29.9  # first node has 29.9 seconds to run
            self.root.build_tree()
            self.root = self.root.find_best_child()
            self.root.time_limit = 1.95  # reset to 2 second limit for root and all its children 
            for child in self.root.children:
                child.time_limit = 1.95
            return self.root.get_move()
        
        
        # if root instantiated, use tree structure to find children representing new game state
        else: 
            found = False
            curTime = time.time()
            for child in self.root.children: # get child that represents new game state
                if (adv_pos == child.adv_pos and my_pos == child.my_pos and self.compare(chess_board, child.chess_board)):
                    self.root = child
                    self.root.parent = None
                    self.root.this_time = curTime # reset time
                    found = True
                    break
            # if not found, create new root
            if (not found):
                self.root = MCTSNode(None, deepcopy(my_pos), deepcopy(adv_pos), max_step, deepcopy(chess_board), None, True)
                self.root.this_time = curTime
                
            # build tree, find move.
            self.root.build_tree()
            self.root = self.root.find_best_child()
            return self.root.get_move()


class MCTSNode: 
        def __init__(self, parent, my_pos, adv_pos, max_step, chess_board, move, my_turn, depth = 1):
            self.parent = parent
            self.chess_board = chess_board
            self.times_visited = 0
            self.win_count = 0
            self.depth = depth

            # Trying to implement a sorta simulated annealing with the c constant
            self.c_constant = (math.e**(1/self.depth))-1 # constant for UCT formula
            self.this_time = time.time()
            self.time_limit = 1.95 # seconds
            self.children = []
            self.my_pos = my_pos
            self.adv_pos = adv_pos
            self.max_step = max_step
            self.my_turn = my_turn
            self.move = move
            self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
            }
            # Moves (Up, Right, Down, Left)
            self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
            # Opposite Directions
            self.opposites = {0: 2, 1: 3, 2: 0, 3: 1}
            
            # TODO: Can play with these values to determine what works best
            self.simulations_per_expanded_child = 3
        
        """
        Recursively update result from child node to parent. 
        """
        def propogate_result(self, result):
            self.win_count += result[0]
            self.times_visited += result[1]

            if (self.parent != None):
                self.parent.propogate_result(result)
            
        """
        Select a child of this node to pick to explore. 
        """
        def select_child(self):
            best_child = None
            best_value = 0
            for child in self.children:
                child.this_time = self.this_time # reset time as selecting children
                if (child.times_visited == 0): # If expanded node that hasn't yet been visited
                    return child
                # select child differently depending on whos turn
                if (self.my_turn):
                    child_value = child.win_count / child.times_visited + (self.c_constant * math.sqrt(math.log(self.times_visited) / child.times_visited))
                else: 
                    child_value = (child.times_visited - child.win_count) / child.times_visited + (self.c_constant * math.sqrt(math.log(self.times_visited) / child.times_visited))

                # get best child
                if (child_value >= best_value):
                    best_value = child_value
                    best_child = child
            return best_child

        """
        Determine if can take one step from current position in the direction specified. 
        """
        def canMoveInDirection(self, board, current_position, adversary_position, direction):
            # If could place a barrier in this direction, could move in that direction given adversary is not there.
            if (not self.canPlaceBarrier(board, current_position, direction)): 
                return False
            else:
                # u
                if (self.dir_map[direction] == 0):
                    return current_position[0] - 1 != adversary_position[0] or current_position[1] != adversary_position[1]
                # r
                if (self.dir_map[direction] == 1):
                    return current_position[0] != adversary_position[0] or current_position[1] + 1 != adversary_position[1]
                # d
                if (self.dir_map[direction] == 2):
                    return current_position[0] + 1 != adversary_position[0] or current_position[1] != adversary_position[1]
                # l
                if (self.dir_map[direction] == 3):
                    return current_position[0] != adversary_position[0] or current_position[1] - 1 != adversary_position[1]

        """
        Determine if can place a barrier in the current_position & specified direction. 
        """
        def canPlaceBarrier(self, board, current_position, direction): 
            # check valid position
            if not self.validPosition(board, current_position):
                return False
            # Check status of board.
            return (not board[current_position[0], current_position[1], self.dir_map[direction]])

        """
        Determine if this is a valid position or not. 
        """
        def validPosition(self, board, position):
            return (position[0] >= 0 and position[1] >= 0 and position[0] < len(board) and position[1] < len(board))

        """
        Get all children moves for this node. 
        """
        def expand(self):
            moveStack = deque() # keep track of moves not expanded
            positionsConsidered = deque() # revisit list (avoid revisiting positions)

            if (self.my_turn):
                moveStack.append((deepcopy(self.my_pos[0]), deepcopy(self.my_pos[1]), 0)) # tuples in moveStack of the form (x, y), depth from start
            else:
                moveStack.append((deepcopy(self.adv_pos[0]), deepcopy(self.adv_pos[1]), 0)) # tuples in moveStack of the form (x, y), depth from start

            # Add timeout here 
            while (time.time() - self.this_time < self.time_limit and moveStack): # while still moves to be considered
                moveBeingConsidered = moveStack.pop()
                positionOfMoveBeingConsidered = (moveBeingConsidered[0], moveBeingConsidered[1])
                moveDepth = moveBeingConsidered[2]

                positionsConsidered.append(positionOfMoveBeingConsidered) # add this to revisit list

                for key in self.dir_map: # add all possible barriers
                    if (self.canPlaceBarrier(self.chess_board, positionOfMoveBeingConsidered, key)): # Can place a barrier here.
                        new_board = deepcopy(self.chess_board)
                        
                        new_board[positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1], self.dir_map[key]] = True
                        # Set the opposite barrier to True
                        move = self.moves[self.dir_map[key]]
                        new_board[positionOfMoveBeingConsidered[0] + move[0], positionOfMoveBeingConsidered[1] + move[1], self.opposites[self.dir_map[key]]] = True

                        if (self.my_turn): # add different nodes depending on whos turn this node represents
            
                            child = MCTSNode(self, deepcopy(positionOfMoveBeingConsidered), deepcopy(self.adv_pos), self.max_step, new_board, (positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1], self.dir_map[key]), not self.my_turn, self.depth+1) # note flip my_pos, adv_pos, flip who's turn
                            child.this_time = self.this_time
                            self.children.append(child) # add viable move to children
                        else:
                            child = MCTSNode(self, self.my_pos, deepcopy(positionOfMoveBeingConsidered), self.max_step, new_board, (positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1], self.dir_map[key]), not self.my_turn, self.depth+1 ) # note flip my_pos, adv_pos, flip who's turn
                            child.this_time = self.this_time
                            self.children.append(child) 
                        
                if (moveBeingConsidered[2] < self.max_step): # expand this move further if not at max moves 
                    for key in self.dir_map: # iterate over directions that could move from this cell. 
                        opponent = self.adv_pos if self.my_turn else self.my_pos # determine who opponent is for this iteration
                        if (self.canMoveInDirection(self.chess_board, positionOfMoveBeingConsidered, opponent, key)): # Add to move stack all possible moves that have not been expanded yet
                            # up
                            if self.dir_map[key] == 0 and (positionOfMoveBeingConsidered[0] - 1, positionOfMoveBeingConsidered[1]) not in positionsConsidered:
                                moveStack.append((positionOfMoveBeingConsidered[0] - 1, positionOfMoveBeingConsidered[1], moveDepth + 1)) # add this move to the stack 
                            # right
                            if self.dir_map[key] == 1 and (positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1] + 1) not in positionsConsidered:
                                 moveStack.append((positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1] + 1, moveDepth + 1)) # add this move to the stack 
                            # down 
                            if self.dir_map[key] == 2 and (positionOfMoveBeingConsidered[0] + 1, positionOfMoveBeingConsidered[1]) not in positionsConsidered:
                                 moveStack.append((positionOfMoveBeingConsidered[0] + 1, positionOfMoveBeingConsidered[1], moveDepth + 1)) # add this move to the stack 
                            # left
                            if self.dir_map[key] == 3 and (positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1] - 1) not in positionsConsidered:
                                 moveStack.append((positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1] - 1, moveDepth + 1)) # add this move to the stack 

        
        def check_endgame(self, board, board_size, player_1, player_2):
            """
            Check if the game ends and compute the current score of the agents.

            Returns
            -------
            is_endgame : bool
                Whether the game ends.
            player_1_score : int
                The score of player 1.
            player_2_score : int
                The score of player 2.
            """
            # Union-Find
            father = dict()
            for r in range(board_size):
                for c in range(board_size):
                    father[(r, c)] = (r, c)

            def find(pos):
                if father[pos] != pos:
                    father[pos] = find(father[pos])
                return father[pos]

            def union(pos1, pos2):
                father[pos1] = pos2

            for r in range(board_size):
                for c in range(board_size):
                    for dir, move in enumerate(
                        self.moves[1:3]
                    ):  # Only check down and right
                        if board[r, c, dir + 1]:
                            continue
                        pos_a = find((r, c))
                        pos_b = find((r + move[0], c + move[1]))
                        if pos_a != pos_b:
                            union(pos_a, pos_b)

            for r in range(board_size):
                for c in range(board_size):
                    find((r, c))
            p0_r = find(player_1)
            p1_r = find(player_2)
            p0_score = list(father.values()).count(p0_r)
            p1_score = list(father.values()).count(p1_r)
            if p0_r == p1_r:
                return False, p0_score, p1_score
            return True, p0_score, p1_score
        
        """
        Run a simulation given the current board state. 
        """
        def run_simulation(self):
            agents_turn = self.my_turn
            turn_player = None
            other_player = None

            # determine who should make initial move in simulation based on whos turn it is
            if (self.my_turn): 
                turn_player = deepcopy(self.my_pos)
                other_player = deepcopy(self.adv_pos)
            else: 
                turn_player = deepcopy(self.adv_pos)
                other_player = deepcopy(self.my_pos)

            board = deepcopy(self.chess_board)

            
            # Run simulation while game not over
            # Time out here 

            while (True): # time out after 0.1 seconds
                if (time.time() - self.this_time >= self.time_limit): # surpassed time
                    return None
                # check if game finished
                results = self.check_endgame(board, len(board), turn_player, other_player)
                if (results[0]):
                    break
                pos_x, pos_y, dir = self.make_random_move(board, turn_player, other_player) # return random move for this player 
                # switch whos turn it is
                turn_player = deepcopy(other_player)
                other_player = (pos_x, pos_y)
                agents_turn = not agents_turn

                # place barrier
                board[pos_x, pos_y, dir] = True
                move = self.moves[dir]
                board[pos_x + move[0], pos_y + move[1], self.opposites[dir]] = True

                

            # if game over, handle result
            f, p0_score, p1_score = self.check_endgame(board, len(board), turn_player, other_player)

            # return score depeneding on whos turn was last played, and who winner was
            if (agents_turn):
                if p0_score > p1_score:
                    return 1
                if p0_score == p1_score:
                    return 0.5
                else:
                    return 0
            else:
                if p0_score > p1_score:
                    return 0
                if p0_score == p1_score:
                    return 0.5
                if p0_score < p1_score:
                    return 1
        
        """
        Determine if this player is stuck (cannot move in any direction)
        """
        def stuck(self, board, turn_player, other_player):
            return (not self.canMoveInDirection(board, turn_player, other_player, "u") and not self.canMoveInDirection(board, turn_player, other_player, "d") 
            and not self.canMoveInDirection(board, turn_player, other_player, "l") and not self.canMoveInDirection(board, turn_player, other_player, "r"))
                

        """
        Make a random move in the simulation.
        """
        def make_random_move(self, board, turn_player, other_player):
            # if stuck (can't move, find where to put barrier)
            if (self.stuck(board, turn_player, other_player)):
                dir = random.choice(["u", "d", "l", "r"])
                while (not self.canPlaceBarrier(board, turn_player, dir)):
                    dir = random.choice(["u", "d", "l", "r"])
                return turn_player[0], turn_player[1], self.dir_map[dir]
            
            # get random number of steps 
            new_move = deepcopy(turn_player)

            steps = random.randint(0, self.max_step)

            dir = None
            
            # make random move while less than steps amount of move
            for _ in range(steps):
                dir = random.choice(["u", "d", "l", "r"])
                while (not self.canMoveInDirection(board, new_move, other_player, dir)):
                    dir = random.choice(["u", "d", "l", "r"])
                # up    
                if (self.dir_map[dir] == 0):
                    new_move = (new_move[0] - 1, new_move[1])
                # right 
                if (self.dir_map[dir] == 1):
                    new_move = (new_move[0], new_move[1] + 1)
                # down 
                if (self.dir_map[dir] == 2):
                    new_move = (new_move[0] + 1, new_move[1])
                # left
                if (self.dir_map[dir] == 3):
                    new_move = (new_move[0], new_move[1] - 1)
            
            # find random direction to place a barrier
            dir = random.choice(["u", "d", "l", "r"])
            while (not self.canPlaceBarrier(board, new_move, dir)):
                dir = random.choice(["u", "d", "l", "r"])
                
            return new_move[0], new_move[1], self.dir_map[dir]

        """
        Build the tree using selection, expansion, simulation, and back propogation.
        """
        def build_tree(self):
            while (time.time() - self.this_time < self.time_limit): #Tree depth 
                selected_node = self

                # select nodes
                while (len(selected_node.children) != 0):
                    selected_node = selected_node.select_child()

                # expand children of leaf node that was selected
                selected_node.expand()

                # run simulation and propogate result
                for child in selected_node.children: 
                    result = 0
                    for _ in range(0,self.simulations_per_expanded_child):
                        outcome = child.run_simulation()
                        if (outcome is not None):
                            result += outcome # run simulations sim_run amount of times
                    child.propogate_result((result, self.simulations_per_expanded_child)) # propogate result back up to node
            

        """
        Find the best child of this node.
        """
        def find_best_child(self):
            
            best_child = None
            best_value = 0
            
            for c in self.children:
                if c.win_count / c.times_visited >= best_value:
                    best_child = c
                    best_value = c.win_count / c.times_visited

            return best_child

        """
        Return move of this node.
        """
        def get_move(self):
            return (self.move[0], self.move[1]), self.move[2]





                
            
       
        
       
    
   
        
        
        
            

   



