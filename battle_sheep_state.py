import numpy as np

# class Cell:
#     def __init__(self, val, sheep_val):
#         self.val = val
#         self.sheep_val = sheep_val

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
    
    player = [i for i in range(1, 5)]

    def __init__(self, state, sheep_state, next_move_player=1):
        self.board = state
        self.sheep_state = sheep_state
        self.board_size = state.shape[0]
        self.next_move_player = next_move_player

    def is_move_legal(self, move):
#         if move.move_player != self.next_move_player:
#             return False

        if not (0 <= move.i < self.board_size):
            return False

        if not (0 <= move.j < self.board_size):
            return False

        if move.d == -1 and self.board[move.i][move.j] == 0:
            for d in range(6):
                new_i = move.i + direction[move.i&1][d][0]
                new_j = move.j + direction[move.i&1][d][1]
                if not (0 <= new_i < self.board_size):
                    return True
                if not (0 <= new_j < self.board_size):
                    return True
                if self.board[new_i][new_j] == -1:
                    return True
            return False

        if move.m >= self.sheep_state[move.i][move.j]:
            return False

        new_i = move.i + direction[move.i&1][move.d][0]
        new_j = move.j + direction[move.i&1][move.d][1]

        if not (0 <= new_i < self.board_size):
            return False

        if not (0 <= new_j < self.board_size):
            return False

        if self.board[new_i][new_j] != 0:
            return False

        return move.move_player == self.board[move.i][move.j]

    @property
    def availiable_player(self):

        availiable = np.ones(4, dtype='bool')

        for player in self.player:
            indices = np.array(np.where(self.board == player)).T
            for i, j in indices:
                availiable[player - 1] = 0
                for d in range(6):
                    if self.is_move_legal(BattleSheepMove(player, i, j, d, 1)):
                        availiable[player - 1] = 1
                        break
                if availiable[player - 1]:
                    break

        return availiable    

    @property
    def game_current_score(self):
        score = np.zeros(4, dtype='int32')
        group = np.zeros((12, 12))
        group_index = 1
        for player in self.player:
            indices = np.array(np.where(self.board == player)).T
            score[player - 1] = 3*len(indices)
            for i, j in indices:
                for d in range(3):
                    new_i, new_j = i + direction[i&1][d][0], j + direction[i&1][d][1]
                    if not (0 <= new_i < self.board_size):
                        continue
                    if not (0 <= new_j < self.board_size):
                        continue
                    if self.board[new_i][new_j] == player:
                        group[i][j] = group[new_i][new_j]
                        break
                if group[i][j] == 0:
                    group[i][j] = group_index
                    group_index += 1
            group_unique, count = np.unique(group[self.board == player], return_counts=True)
            if len(count):
                score[player - 1] += np.max(count)

        return score

    def is_game_over(self):
        return not self.availiable_player.any()

    def walk(self, i, j, d):
        while True:
            new_i, new_j = i + direction[i&1][d][0], j + direction[i&1][d][1]
            if not (0 <= new_i < self.board_size):
                return i, j
            if not (0 <= new_j < self.board_size):
                return i, j
            if self.board[new_i][new_j] != 0:
                return i, j

            i = new_i
            j = new_j

    def move(self, move):
        new_board = np.copy(self.board)
        new_sheep_state = np.copy(self.sheep_state)
        next_move_player = (self.next_move_player&3) + 1
        
        if move.i == -1 and move.j == -1:
            return BattleSheepState(new_board, new_sheep_state, next_move_player)

        if not self.is_move_legal(move):
            raise ValueError('illegal move:\n{}'.format(move))

        if move.d == -1:
            new_i, new_j = move.i, move.j
        else:
            new_i, new_j = self.walk(move.i, move.j, move.d)

        new_board[new_i][new_j] = self.next_move_player
        new_sheep_state[move.i][move.j] -= move.m
        new_sheep_state[new_i][new_j] = move.m

        return BattleSheepState(new_board, new_sheep_state, next_move_player)

    def get_legal_actions(self):
        indices = np.array(np.where(self.board == self.next_move_player)).T
        legal_action = []

        if len(indices) == 0:
            indices = np.array(np.where(self.board == 0)).T
            for i, j in indices:
                action = BattleSheepMove(self.next_move_player, i, j)
                if self.is_move_legal(action):
                    legal_action.append(action)
            return legal_action

        for i, j in indices:
            for d in range(6):
                for m in range(1, self.sheep_state[i][j]):
                    action = BattleSheepMove(self.next_move_player, i, j, d, m)
                    if not self.is_move_legal(action):
                        break
                    legal_action.append(action)

        if len(legal_action):
            return legal_action

        return [BattleSheepMove(self.next_move_player)]

if __name__ == '__main__':
    state = np.zeros((12, 12), dtype='int32')
    sheep_state = np.zeros((12, 12), dtype='int32')
    player = np.random.randint(1, 5)
    test = BattleSheepState(state, sheep_state, player)
    while not test.is_game_over():
        legal_action = np.random.choice(test.get_legal_actions(), 1)
        print(legal_action[0])
        test = test.move(legal_action[0])
    print(test.game_current_score)
