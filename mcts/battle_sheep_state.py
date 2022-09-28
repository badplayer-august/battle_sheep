import time
import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

get_legal_actions_time = 0
get_random_action = 0
move_time = 0

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
    def __init__(self, state, sheep_state, next_move_player=1):
        self.board = np.array(state)
        self.sheep_state = sheep_state
        self.board_size = state.shape[0]
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
                    if self.dir[d][i][j] == self.board[i][j]:
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
            legal_cell = (self.board == 0) & (self.dir == -1).any(axis=0)
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
    
    def render_board(self, board):
        data = []
        for i in range(12):
            for j in range(12):
                if i&1:
                    data.append([i, j+0.5, board[i][j]])
                else:
                    data.append([i, j, board[i][j]])
        df = pd.DataFrame(data, columns=['y', 'x', 'label'])
        return sns.scatterplot(data=df, x='x', y='y', hue='label')

    def render(self, show_dir=False):
        plot = self.render_board(self.board)
        for i in range(12):
            for j in range(12):
                plot.annotate(str(self.sheep_state[i][j]), xy=(j+0.5 if i&1 else j, i), horizontalalignment='center')
        plt.gca().invert_yaxis()
        plt.show()
        if show_dir:
            for d in self.dir:
                self.render_board(d)
                plt.gca().invert_yaxis()
                plt.show()




if __name__ == '__main__':
    for i in range(10):
        state = np.zeros((12, 12), dtype='int32')
        sheep_state = np.zeros((12, 12), dtype='int32')
        player = np.random.randint(1, 5)
        test = BattleSheepState(state, sheep_state, player)
        while not test.is_game_over():
            start = time.time()
            temp = test.get_legal_actions()
            end = time.time()
            get_legal_actions_time += (end - start)
            start = time.time()
            action_num = len(temp)
            randint = random.getrandbits(7)
            while randint >= action_num:
                randint = random.getrandbits(7)
            legal_action = temp[randint]
            # legal_action = np.random.choice(temp, 1)
            end = time.time()
            get_random_action += (end - start)
#           print(test.game_current_score)
#           test.render(False)
#           print(legal_action[0])
            start = time.time()
            test = test.move(legal_action)
            end = time.time()
            move_time += (end - start)
        print(test.game_current_score)
        print((test.game_current_score-np.min(test.game_current_score))/np.sum(test.game_current_score - np.min(test.game_current_score)))
        print(np.exp(test.game_current_score)/np.sum(np.exp(test.game_current_score)))
    print('get_legal_actions_time: ', get_legal_actions_time)
    print('get_random_action_time:', get_random_action)
    print('move_time: ', move_time)
