# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
from copy import deepcopy
import sys


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

    class MCTSNode: 
        def __init__(self, parent, my_pos, adv_pos, max_step, chess_board, move, my_turn):
            self.parent = parent
            self.chess_board = chess_board
            self.move = move
            self.times_visited = 0
            self.win_count = 0
            self.children = []
            self.my_pos = my_pos
            self.adv_pos = adv_pos
            self.max_step = max_step
            self.my_turn = my_turn
            self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
            }
            
        
        """
        Determine if can take one step from current position to the cell in direction 'direction'
        """
        def canMove(self, current_position, direction):
            # Check if we can move in direction from current_position by checking that it is 'clear' and opponent is not there. 
            return (not self.chess_board[current_position[0], current_position[1], self.dir_map[direction]] 
            and (current_position[0] != self.adv_pos[0] and current_position[1] != self.adv_pos[1]))
            

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
        # dummy return
        return my_pos, self.dir_map["u"]

   



