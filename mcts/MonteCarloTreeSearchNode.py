import numpy as np
from collections import defaultdict
from abc import ABC,abstractmethod
class MonteCarloTreeSearchNode(ABC):
    def __init__(self,state,parent=None):
        self.state = state
        self.parent = parent
        self.children = []

    @property
    @abstractmethod
    def untried_actions(self):
        pass
    @property
    @abstractmethod    
    def q(self):
        pass
    @property
    @abstractmethod
    def n(self):
        pass
    @abstractmethod
    def expand(self):
        pass
    @abstractmethod
    def is_terminal_node(self):
        pass
    @abstractmethod
    def rollout(self):
        pass
    @abstractmethod
    def backpropagate(self):
        pass
    def is_fully_expanded(self):
        return len(self.untried_actions)
    def best_child(self,c_param=1.4):    
        weights = [ (c.q / c.n) + c_param * np.sqrt(( np.log(self.n) / c.n)) for c in self.children]
        return self.children[np.argmax(weights)]
    def rollout_policy(self,possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]