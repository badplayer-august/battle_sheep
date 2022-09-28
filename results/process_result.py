import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_point(score):
    rank_score = np.array([5, 3, 2, 1])
    arg = np.argsort(score)
    ms = 65
    ranks = [0, 0, 0, 0]
    rank = 0
    cnt = {1: 0, 2: 0, 3: 0, 4: 0}
    for i, a in enumerate(arg[::-1]):
        print(i)
        if ms > score[a]:
            ms = score[a]
            rank = i + 1
        ranks[a] = rank
        cnt[rank] += 1
    points = []
    for rank in ranks:
        c = cnt[rank]
        point = np.sum(rank_score[rank-1:rank-1+c])/c
        points.append(point)
    return ranks, points
    

sns.set_theme(style="darkgrid")

data = pd.read_csv('./result.csv')
new_data = []
match = 0
for row in data.iloc:
    rank, point = get_point(row[['p1_score', 'p2_score', 'p3_score', 'p4_score']])
    for player in range(4):
        new_data.append([str(player+1), row['p'+str(player+1)], row['p'+str(player+1)+'_score'], rank[player], point[player], match])
    print(row, new_data[-4:])
    match += 1
new_data = pd.DataFrame(new_data, columns=['player', 'id', 'score', 'rank', 'point', 'match'])
new_data.to_csv('match_result.csv', index=None)
sns.lineplot(data=new_data.groupby(['player', 'score']).count().reset_index(), x='score', y='id', hue='player')
plt.show()
