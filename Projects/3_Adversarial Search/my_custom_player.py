from sample_players import DataPlayer
import random


class CustomPlayer(DataPlayer):
    """ Implement your own agent to play knight's Isolation

    The get_action() method is the only *required* method. You can modify
    the interface for get_action by adding named parameters with default
    values, but the function MUST remain compatible with the default
    interface.

    **********************************************************************
    NOTES:
    - You should **ONLY** call methods defined on your agent class during
      search; do **NOT** add or call functions outside the player class.
      The isolation library wraps each method of this class to interrupt
      search when the time limit expires, but the wrapper only affects
      methods defined on this class.

    - The test cases will NOT be run on a machine with GPU access, nor be
      suitable for using any other machine learning techniques.
    **********************************************************************
    """
    
    def get_action(self, state):
        """ Employ an adversarial search technique to choose an action
        available in the current state calls self.queue.put(ACTION) at least

        This method must call self.queue.put(ACTION) at least once, and may
        call it as many times as you want; the caller is responsible for
        cutting off the function after the search time limit has expired. 

        See RandomPlayer and GreedyPlayer in sample_players for more examples.

        **********************************************************************
        NOTE: 
        - The caller is responsible for cutting off search, so calling
          get_action() from your own code will create an infinite loop!
          Refer to (and use!) the Isolation.play() function to run games.
        **********************************************************************
        """
        # TODO: Replace the example implementation below with your own search
        #       method by combining techniques from lecture
        #
        # EXAMPLE: choose a random move without any search--this function MUST
        #          call self.queue.put(ACTION) at least once before time expires
        #          (the timer is automatically managed for you)        
        move = None
        if state.ply_count <= 1:
            move = random.choice(state.actions()) # Random Move
        else:
            move = self.alpha_beta_search(state, depth = 1 ) # 1, 3, 7, 10
        self.queue.put(move)
        
    def alpha_beta_search(self, gameState, depth):
        alpha = float("-inf")
        beta = float("inf")
        best_score = float("-inf")
        best_move = random.choice(gameState.actions()) # initialization
        
        for a in gameState.actions():
            v = self.min_value(gameState.result(a), alpha, beta, depth)
            alpha = max(alpha, v)
            if v > best_score:
                best_score = v
                best_move = a
                
        return best_move

    def min_value(self, gameState, alpha, beta, depth):
        if gameState.terminal_test() or depth <= 0:
            player_1 = None
            player_2 = None
            
            if self.player_id == 0:
                player_1 = 0
                player_2 = 1
            else:
                player_1 = 1
                player_2 = 0
                
            p1_liberties = gameState.liberties(gameState.locs[player_1])
            p2_liberties = gameState.liberties(gameState.locs[player_2])
            
            v = float("inf")
            if len(p1_liberties) < len(p2_liberties):
                v = (2*len(p1_liberties)) - len(p2_liberties)
            else:
                v = len(p1_liberties) - (2*len(p2_liberties))

            return v
        
        v = float("inf")
        
        for a in gameState.actions():
            v = min(v, self.max_value(gameState.result(a), alpha, beta, depth - 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
            
        return v


    def max_value(self, gameState, alpha, beta, depth):
        if gameState.terminal_test() or depth <= 0:
            player_1 = None
            player_2 = None
            
            if self.player_id == 0:
                player_1 = 0
                player_2 = 1
            else:
                player_1 = 1
                player_2 = 0
                
            p1_liberties = gameState.liberties(gameState.locs[player_1])
            p2_liberties = gameState.liberties(gameState.locs[player_2])
            
            v = float("inf")
            if len(p1_liberties) < len(p2_liberties):
                v = (2*len(p1_liberties)) - len(p2_liberties)
            else:
                v = len(p1_liberties) - (2*len(p2_liberties))
                
            return v
        
        v = float("-inf")
        for a in gameState.actions():
            v = max(v, self.min_value(gameState.result(a), alpha, beta, depth - 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
            
        return v
