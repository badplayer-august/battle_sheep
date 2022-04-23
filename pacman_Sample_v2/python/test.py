import numpy as np
import time


direction = [
    [0, -1],
    [0, 1],
    [-1, 0],
    [1, 0],
]

h_wall = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
    [1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

v_wall =[
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
    [1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1]
] 

h_wall = np.array(h_wall, dtype='bool')
v_wall = np.array(v_wall, dtype='bool')
wall = np.zeros((4, 16, 16), dtype='bool')
wall[0,:,:] = v_wall[:,:16]
wall[1,:,:] = v_wall[:,1:]
wall[2,:,:] = h_wall[:16,:]
wall[3,:,:] = h_wall[1:,:]

dis_map_bfs = list(np.ones((16, 16, 16, 16), dtype='int32')*-1)
wall = list(wall)

bfs_start = time.time()
for i in range(1):
    for j in range(1):
        queue = [(i, j, 0)]
        dis_map_bfs[i][j][i][j] = 0
        while len(queue):
            x, y, dis = queue.pop(0)
            for n, d in enumerate(direction):
                nx, ny = x + d[0], y + d[1]
                if 0 <= nx < 16 and 0 <= ny < 16 and wall[n][x][y]==False and dis_map_bfs[i][j][nx][ny] == -1:
                    dis_map_bfs[i][j][nx][ny] = dis + 1
                    queue.append((nx, ny, dis+1))
bfs_end = time.time()
print(bfs_end-bfs_start)

dis_map_block = np.ones((16, 16, 16, 16), dtype='int32')*-1
wall = np.array(wall)

block_start = time.time()
for i in range(1):
    for j in range(1):
        dis = 0
        dis_map_block[i][j][i][j] = dis
        mask = np.zeros((18, 18), dtype='bool')
        mask[i + 1][j + 1] = True
        while not mask[1:17, 1:17].all():
            dis += 1
            l = mask[1:17, 2:] & ~wall[1]
            r = mask[1:17, :16] & ~wall[0]
            u = mask[2:, 1:17] & ~wall[3]
            d = mask[:16, 1:17] & ~wall[2]
            dis_map_block[i][j][(l | r | u | d) & ~mask[1:17, 1:17]] = dis
            mask[1:17, 1:17] = dis_map_block[i][j] != -1

block_end = time.time()
print(block_end - block_start)

while True:
    i = int(input('i: '))
    j = int(input('j: '))
    print(dis_map_bfs[i][j])
    print(dis_map_block[i][j])
