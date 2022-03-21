import random
import numpy as np
import pygame
from pygame import gfxdraw
import matplotlib.pyplot as plt

class battle_sheep:
    r = 20
    color=[(102, 102, 102), (255, 255, 255), (255, 145, 145), (255, 245, 106), (100, 211, 128), (95, 138, 238)]
    screen = None
    screen_width = 500
    screen_height = 480

    player = [None for _ in range(4)]
    alive = np.ones((4), dtype='bool')
    map_stat = np.zeros((12, 12), dtype='int32')    
    sheep_stat = np.zeros((12, 12), dtype='int32')
    connect_cell = set()
    #  1 2
    # 3 x 4
    #  5 6
    dir = [
        # row is even
        [
            [-1, -1],
            [-1, 0],
            [0, -1],
            [0, 1],
            [1, -1],
            [1, 0],
        ],
        # row is odd
        [
            [-1, 0],
            [-1, 1],
            [0, -1],
            [0, 1],
            [1, 0],
            [1, 1],
        ],
    ]

    def add_cell(self, i, j):
        dir = self.dir[i&1]
        self.map_stat[i][j] = 0

        for dir_i, dir_j in dir:
            new_i, new_j = i + dir_i, j + dir_j
            if 0 <= new_i and new_i < 12 and 0 <= new_j and new_j < 12 and self.map_stat[new_i][new_j] == -1:
                self.connect_cell.add((new_i, new_j))

        return

    def init_game(self):
        self.map_stat[:] = -1    
        self.sheep_stat[:] = 0    
        self.connect_cell = set()

        i, j = np.random.randint(5, 7, 2)
        self.add_cell(i, j)

        for _ in range(63):
            i, j = random.sample(self.connect_cell, k=1)[0]
            self.connect_cell.remove((i, j))
            self.add_cell(i, j)

    def render(self):
        if self.screen == None:
            pygame.init()
            pygame.display.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.surf = pygame.Surface((self.screen_width, self.screen_height))
        self.surf.fill((255, 255, 255))
        self.screen.blit(self.surf, (0, 0))

        for i in range(12):
            self.row = pygame.Surface((24*self.r, 2*self.r))
            self.row.fill((255, 255, 255))
            self.row.set_colorkey((255, 255, 255))
            for j in range(12):
                gfxdraw.filled_circle(self.row, int(j*2*self.r + self.r), int(self.r), int(self.r), self.color[self.map_stat[i][j] + 1])
                gfxdraw.circle(self.row, int(j*2*self.r + self.r), int(self.r), int(self.r), self.color[0])
            self.screen.blit(self.row, (int((i&1)*self.r), int(i*2*self.r)), special_flags=pygame.BLEND_RGB_MIN)
            self.row.set_alpha(75)
        pygame.display.flip()

    def add_players(self, p1, p2, p3, p4):
        self.player = np.array([p1, p2, p3, p4])

    def play_one_game():
        self.alive[:] = 1
        np.random.shuffle(self.player)

        for p in range(4):
            i, j = self.player[i].InitPos(self.map_stat)
            self.add_init_stat(i, j, p)

        while len(self.alive[self.alive]):
            for p in range(4):
                if self.not_alive(p):
                    continue
                i, j, m, d = self.player[p].GetStep(p + 1, self.map_stat, self.sheep_stat)
                self.walk(i, j, m, d, p)

    def not_alive(self, p):
        pass

    def add_init_stat(self, i, j, p):
        pass

    def walk(self, i, j, m, d, p):
        pass


if __name__ == '__main__':
    test = battle_sheep()
    test.init_game()
    while True:
        test.render()
