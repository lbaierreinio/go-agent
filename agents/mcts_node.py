from copy import deepcopy

class MCTSNode: 
        def __init__(self, parent, my_pos, adv_pos, max_step, chess_board, my_turn):
            self.parent = parent
            self.chess_board = chess_board
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
        Determine if can take one step from current position in the direction specified. 
        """
        def canMoveInDirection(self, current_position, direction):
            # If could place a barrier in this direction, could move in that direction given adversary is not there.
            return (self.canPlaceBarrier(current_position, direction) and (current_position[0] != self.adv_pos[0] and current_position[1] != self.adv_pos[1]))

        """
        Determine if can place a barrier in the current_position & specified direction. 
        """
        def canPlaceBarrier(self, current_position, direction): 
            # check valid position
            if not self.validPosition(current_position):
                return False
            # Check status of board.
            return (not self.chess_board[current_position[0], current_position[1], self.dir_map[direction]])


        """
        Determine if this is a valid position or not. 
        """
        def validPosition(self, position):
            return not (position[0] < 0 or position[1] < 0 or position[0] >= self.chess_board.size or position[1] >= self.chess_board.size)

        """
        Get all children moves for this node. 
        """
        def expand(self):
            moveStack = [] # keep track of moves not expanded
            positionsConsidered = [] # revisit list (avoid revisiting positions)

            moveStack.append((self.my_pos[0], self.my_pos[1], 0)) # tuples in moveStack of the form (x, y), depth from start

            while (moveStack): # while still moves to be considered
                moveBeingConsidered = moveStack.pop()
                positionOfMoveBeingConsidered = (moveBeingConsidered[0], moveBeingConsidered[1])
                moveDepth = moveBeingConsidered[2]

                positionsConsidered.append(positionOfMoveBeingConsidered) # add this to revisit list

                for key in self.dir_map: # add all possible barriers
                    if (self.canPlaceBarrier(positionOfMoveBeingConsidered, key)): # Can place a barrier here.
                        new_board = deepcopy(self.chess_board)
                        new_board[positionOfMoveBeingConsidered[0], positionOfMoveBeingConsidered[1], self.dir_map[key]] = False # indicate barrier was placed
                        child = MCTSNode(self, self.adv_pos, positionOfMoveBeingConsidered, self.max_step, new_board, not self.my_turn ) # note flip my_pos, adv_pos, flip who's turn
                        self.children.append(child) # add viable move to children
                        
                if (moveBeingConsidered[2] < self.max_step): # expand this move further if not at max moves 
                    for key in self.dir_map: # iterate over directions that could move from this cell. 
                        if (self.canMoveInDirection(positionOfMoveBeingConsidered, key)): # Add to move stack all possible moves that have not been expanded yet
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