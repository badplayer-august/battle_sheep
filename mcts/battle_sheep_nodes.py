import numpy as np
import random

class MCTS_NODE:
    def __init__(self, player, state, parent=None):
        self.player = player
        self.state = state
        self.parent = parent
        self.children = []

        self._n_visits = 0
        self._results = np.zeros(4)
        self._untried_actions = None

    @property
    def untried_actions(self):
        if self._untried_actions == None:
            self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions

    @property
    def X(self):
        exp_result = np.exp(self._results - np.min(self._results))
        softmax_result = exp_result/np.sum(exp_result)
        return softmax_result[self.parent.state.next_to_move]

    @property
    def n(self):
        return self._n_visits

    @property
    def q(self):
        return self._results[self.parent.state.next_move_player]

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.move(action)
        child_node = MCTS_NODE(
            next_state, parent=self
        )
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.is_game_over()

    def rollout(self, h=-1):
        current_rollout_state = self.state
        while not current_rollout_state.is_game_over() and h != 0:
            if current_rollout_state.next_move_player == 4:
                h -= 1
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.move(action)
        return current_rollout_state.game_current_score

    def backpropagate(self, result):
        self._n_visits += 1.
        self._results += result
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.4):
        choices_weights = [
            c.X + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):        
        possible_moves_num = len(possible_moves)
        randint = random.getrandbits(7)
        while randint >= possible_moves_num:
            randint = random.getrandbits(7)
        return possible_moves[randint]
