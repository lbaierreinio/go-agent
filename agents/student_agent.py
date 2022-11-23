# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
from agents.mcts_node import MCTSNode
from copy import deepcopy
import time 

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
        # self.MCT; # Monte Carlo Tree

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
            self.root.build_tree(1)
            self.root = self.root.find_best_child()
            return self.root.get_move()
        
        # if root instantiated, use tree structure to find children representing new game state
        else: 
            found = False
            for child in self.root.children: # get child that represents new game state
                if (adv_pos == child.adv_pos and my_pos == child.my_pos and self.compare(chess_board, child.chess_board)):
                    self.root = child
                    self.root.parent = None
                    self.root.this_time = time.time() # reset time
                    found = True
                    break
            # if not found, create new root
            if (not found):
                self.root = MCTSNode(None, deepcopy(my_pos), deepcopy(adv_pos), max_step, deepcopy(chess_board), None, True)
                self.root.this_time = time.time() 
                
            # build tree, find move.
            self.root.build_tree(1)
            self.root = self.root.find_best_child()
            return self.root.get_move()



        
        
       
    
   
        
        
        
            

   



