from MonteCarloTreeSearchNode import MonteCarloTreeSearchNode
import numpy as np
from collections import defaultdict
class BattleSheepMonteCarloTreeNode(MonteCarloTreeSearchNode):
    def __init__(self,state,parent=None):
        super().__init__(state,parent)
        self.number_of_visits = 0.0
        self.untried_action = None
        self.results = defaultdict(int)
    @property
    def untried_actions(self):
        if self.untried_action is None:
            self.untried_action = self.state.get_legal_actions()
        return self.untried_action
    @property
    def q(self):
        player_ID = self.state.next_move_player-1
        if player_ID==0:
            player_ID=4
        return self.results[player_ID]        
    @property
    def n(self):
        return self.number_of_visits
    def is_terminal_node(self):
        return self.state.is_game_over()
    def expand(self):
        action = self.untried_action.pop()
        next_state = self.state.move(action)
        child = BattleSheepMonteCarloTreeNode(next_state,self)
        self.children.append(child)
        return child
    def rollout(self):
        current_state = self.state
        while not current_state.is_game_over()
            possible_moves = current_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_state = self.state.move(action)
        scores = current_state.game_current_score()
        return np.argmax(scores)+1
        ### 再想想
    def backpropagate(self,result):
        self.number_of_visits+=1.0
        self.results[result]+=1.0
        if self.parent:
            return backpropagate(result)
    
    
