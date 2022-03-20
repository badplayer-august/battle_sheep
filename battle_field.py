import numpy as np
import matplotlib.pyplot as plt

class battle_sheep_field:
    def __init__(self):
        self.field = np.zeros((12, 12))
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
        connect_cell = set()
        i, j = np.random.randint(5, 7, 2)
        self.field[i][j] = -1
        for di, dj in dir[i%2]:
            print(di, dj)
            ni, nj = i + di, j + dj
            if 0 <= ni and ni < 12 and 0 <= nj and nj < 12:
                connect_cell.add((ni, nj))

        for _ in range(63):
            success = False
            while not success:
                connect_cell_list = list(connect_cell)
                print(connect_cell_list)
                index = np.random.randint(0, len(connect_cell_list))
                i, j = connect_cell_list[index]
                connect_cell.remove((i, j))
                success = (self.field[i][j] != -1) 
            self.field[i][j] = -1
            for di, dj in dir[i%2]:
                ni, nj = i + di, j + dj
                if 0 <= ni and ni < 12 and 0 <= nj and nj < 12:
                    connect_cell.add((ni, nj))

        for i in range(12):
            for j in range(12):
                self.field[i][j] = -1 - self.field[i][j]

        free_x = []
        free_y = []
        wall_x = []
        wall_y = []
        for i in range(12):
            for j in range(12):
                if self.field[i][j] == 0:
                    if i%2 == 1:
                        j += 0.5
                    free_x.append(i)
                    free_y.append(j)
                else:
                    if i%2 == 1:
                        j += 0.5
                    wall_x.append(i)
                    wall_y.append(j)


        print(self.field)
        fig, ax = plt.subplots() 
        ax.scatter(free_y, free_x, s=500)
        ax.scatter(wall_y, wall_x, s=500)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    battle_sheep_field()
