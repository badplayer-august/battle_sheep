import numpy as np

direction = [
    [0, -1],
    [0, 1],
    [-1, 0],
    [1, 0],
    [0, 0],
]

class Greedy_BFS:
    def __init__(h_wall, v_wall):
        h_wall = np.array(h_wall, dtype='bool')
        v_wall = np.array(v_wall, dtype='bool')
        self.wall = np.zeros((4, 16, 16), dtype='bool')
        self.wall[0,:,:] = v_wall[:16,:]
        self.wall[1,:,:] = v_wall[1:,:]
        self.wall[2,:,:] = h_wall[:,:16]
        self.wall[3,:,:] = h_wall[:,1:]

    def best_step(playerStat, otherPlayerStat, ghostStat, propsStat):
        playerDisMap = get_dis_map(playerStat[1]//25, playerStat[0]//25)

    def get_dis_map():
        pass

    def function():
        pass


