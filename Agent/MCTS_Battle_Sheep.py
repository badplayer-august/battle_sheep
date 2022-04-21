import time
import random
import numpy as np

direction = [
    # row is even
    [
        [-1, -1], [-1, 0],
        [0, -1],[0, 1],
        [1, -1], [1, 0],
    ],
    # row is odd
    [
        [-1, 0],[-1, 1],
        [0, -1],[0, 1],
        [1, 0],[1, 1],
    ],
]

class BattleSheepMove:
    def __init__(self, move_player, i=-1, j=-1, d=-1, m=16):
        self.move_player = move_player
        self.i = i
        self.j = j
        self.d = d
        self.m = m

    def __repr__(self):
        if self.i == -1 and self.j == -1:
            return '[Pass] player:{:1d}'.format(
                self.move_player,
            )
        elif self.d == -1:
            return '[Init] player:{:1d} i:{:2d} j:{:2d}'.format(
                self.move_player,
                self.i,
                self.j,
            )
        else: 
            return '[Move] player:{:1d} i:{:2d} j:{:2d} d:{:2d} m:{:2d}'.format(
                self.move_player,
                self.i,
                self.j,
                self.d,
                self.m,
            )

class BattleSheepState:
    def __init__(self, state, sheep_state, next_move_player):
        self.board = np.array(state)
        # if sheep_state == None:
        #     sheep_state = np.zeros((12, 12))
        #     sheep_state[self.board != 0] = 16
        # if next_move_player == None:
        #     next_move_player = 1
        #     while not (self.board == next_move_player).any():
        #         next_move_player += 1
        self.sheep_state = sheep_state
        self.next_move_player = next_move_player
        self.dir = np.ones((6, 12, 12))*-1
        self.dir[0,2::2,1:] = self.board[1:11:2,:-1]
        self.dir[0,1::2,:] = self.board[::2,:]
        self.dir[1,2::2,:] = self.board[1:11:2,:]
        self.dir[1,1::2,:-1] = self.board[::2,1:]
        self.dir[2,:,1:] = self.board[:,:-1]
        self.dir[3,:,:-1] = self.board[:,1:]
        self.dir[4,::2,1:] = self.board[1::2,:-1]
        self.dir[4,1:-2:2,:] = self.board[2::2,:]
        self.dir[5,::2,:] = self.board[1::2,:]
        self.dir[5,1:-2:2,:-1] = self.board[2::2,1:]

    @property
    def availiable_player(self):
        availiable = np.zeros(4)

        vaild_cell = (self.dir == 0).any(axis=0) & (self.sheep_state != 1)

        for player in range(1, 5):
            player_cell = self.board == player
            availiable[player - 1] = (player_cell.any() == False) | (player_cell & vaild_cell).any()

        return availiable    

    @property
    def game_current_score(self):
        disjoint_set = [[-1 for _ in range(12)] for _ in range(12)]
        for i in range(12):
            for j in range(12):
                for d in range(3):
                    if self.board[i][j] != -1 and self.dir[d][i][j] == self.board[i][j]:
                        value = disjoint_set[i][j]
                        new_i, new_j = i + direction[i&1][d][0], j + direction[i&1][d][1]

                        while disjoint_set[new_i][new_j] >= 0:
                            new_i, new_j = disjoint_set[new_i][new_j] & 15, disjoint_set[new_i][new_j] >> 4

                        if value < 0:
                            disjoint_set[new_i][new_j] += value
                            disjoint_set[i][j] = (new_i | (new_j << 4)) 
                        elif value != (new_i | (new_j << 4)):
                            disjoint_set[value & 15][value >> 4] += disjoint_set[new_i][new_j]
                            disjoint_set[new_i][new_j] = value

        disjoint_set = np.array(disjoint_set)
        score = []
        for player in range(1, 5):
            score.append((self.board==player).sum()*3)
            if score[player - 1]:
                score[player - 1] -= disjoint_set[self.board==player].min()

        return score

    def is_game_over(self):
        return not self.availiable_player.any()

    def walk(self, i, j, d):
        while self.dir[d][i][j] == 0:
            i, j = i + direction[i&1][d][0], j + direction[i&1][d][1]

        return i, j

    def move(self, move):
        new_board = np.copy(self.board)
        new_sheep_state = np.copy(self.sheep_state)
        next_move_player = (self.next_move_player&3) + 1
        
        if move.i == -1 and move.j == -1:
            return BattleSheepState(new_board, new_sheep_state, next_move_player)

        if move.d == -1:
            new_i, new_j = move.i, move.j
        else:
            new_i, new_j = self.walk(move.i, move.j, move.d)

        new_board[new_i][new_j] = self.next_move_player
        new_sheep_state[move.i][move.j] -= move.m
        new_sheep_state[new_i][new_j] = move.m

        return BattleSheepState(new_board, new_sheep_state, next_move_player)

    def get_legal_actions(self):
        player_cell = self.board == self.next_move_player
        legal_action = []

        if player_cell.any() == False:
            mask = np.zeros((12, 12), dtype='bool')
            mask[1:11, 1:11] = True
            legal_cell = (self.board == 0) & (self.dir == -1).any(axis=0) & mask
            indices = np.where(legal_cell)
            for i, j in zip(indices[0], indices[1]):
                legal_action.append(BattleSheepMove(self.next_move_player, i, j))
            return legal_action

        for d in range(6):
            legal_direction = player_cell & (self.dir[d] == 0)
            indices = np.where(legal_direction)
            for i, j in zip(indices[0], indices[1]):
                for m in range(1, self.sheep_state[i][j]):
                    legal_action.append(BattleSheepMove(self.next_move_player, i, j, d, m))
        
        if len(legal_action):
            return legal_action

        return [BattleSheepMove(self.next_move_player)]

class MCTS_NODE:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.children_move = []

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
        result = self._results - np.min(self._results) + 1
        result = np.exp(4*result/np.max(result))
        result = result/np.sum(result)
        return result[self.parent.state.next_move_player - 1]

    @property
    def n(self):
        return self._n_visits

    @property
    def q(self):
        return self._results[self.parent.state.next_move_player - 1]

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.move(action)
        child_node = MCTS_NODE(
            next_state, parent=self
        )
        self.children.append(child_node)
        self.children_move.append(action)
        return child_node

    def is_terminal_node(self):
        return self.state.is_game_over()

    def rollout(self, h):
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

    def best_child(self, c_param):
        choices_weights = [
            c.X + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def best_move(self):
        choices_weights = [
            c.X
            for c in self.children
        ]
        return self.children_move[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):        
        possible_moves_num = len(possible_moves)
        randint = random.getrandbits(7)
        while randint >= possible_moves_num:
            randint = random.getrandbits(7)
        return possible_moves[randint]

class MCTS:
    def __init__(self, node):
        self.root = node

    def best_action(self, simulations_number=None, c_param=1.4, h=-1):
        for _ in range(0, simulations_number):            
            v = self._tree_policy(c_param)
            reward = v.rollout(h)
            v.backpropagate(reward)
        return self.root.best_move()

    def _tree_policy(self, c_param):
        current_node = self.root
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child(c_param)
        return current_node

if __name__ == '__main__':
    state = np.zeros((12, 12), dtype='int32')
    sheep_state = np.zeros((12, 12), dtype='int32')
    cur_state = BattleSheepState(state, sheep_state, 1)
    while not cur_state.is_game_over():
        action = MCTS(MCTS_NODE(cur_state)).best_action(1000)
        cur_state = cur_state.move(action)
        print(cur_state.board)
        print(cur_state.sheep_state)
    print(cur_state.game_current_score)
