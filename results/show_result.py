import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

step_num = [634, 653, 623, 747, 758, 800, 851, 981, 1115, 1243, 1402, 1474, 1877, 2682, 3217, 8333]
step_i = [i for i in range(1, 17)]
df = pd.DataFrame([[n, i] for n, i in zip(step_num, step_i)], columns=['cnt', 'i'])

sns.lineplot(data=df, x='i', y='cnt', markers=True).set(title='Simulation Number', xlabel='Step', ylabel='Count')
plt.savefig('Sim_num.png')
plt.clf()

data = pd.read_csv('./match_result.csv', dtype={'player': 'string', 'id': 'string'})
# sns.lineplot(data=data.groupby(['point', 'player']).count().reset_index(), x='point', y='rank', hue='player')
# plt.show()

print(data.groupby(['player']).mean().reset_index()[['player', 'point', 'score']])
print(data[(data['id'] == '1014') | (data['id'] == '1514')].groupby(['point', 'id']).count().reset_index())

sns.lineplot(data=data[(data['id'] == '1014') | (data['id'] == '1514')].groupby(['point', 'id']).count().reset_index(), x='point', y='rank', hue='id', estimator=None).set(title='Point', xlabel='point', ylabel='count')
plt.savefig('id_point_line.png')
plt.clf()

sns.violinplot(data=data, x='id', y='point', xlim=[1, 5]).set(title='Score')
plt.savefig('id_point_vio.png')
plt.clf()

sns.lineplot(data=data.groupby(['point', 'player']).count().reset_index(), x='point', y='rank', hue='player', estimator=None).set(title='Point', xlabel='point', ylabel='count')
plt.savefig('player_point_line.png')
plt.clf()


sns.lineplot(data=data[data['id'] == '1009'].groupby(['point', 'id', 'player']).count().reset_index(), x='point', y='rank', hue='id', style='player', estimator=None).set(title='Point', xlabel='point', ylabel='count')
plt.savefig('1009_point_line.png')
plt.clf()
sns.lineplot(data=data[data['id'] == '1014'].groupby(['point', 'id', 'player']).count().reset_index(), x='point', y='rank', hue='id', style='player', estimator=None).set(title='Point', xlabel='point', ylabel='count')
plt.savefig('1014_point_line.png')
plt.clf()
sns.lineplot(data=data[data['id'] == '1020'].groupby(['point', 'id', 'player']).count().reset_index(), x='point', y='rank', hue='id', style='player', estimator=None).set(title='Point', xlabel='point', ylabel='count')
plt.savefig('1020_point_line.png')
plt.clf()
sns.lineplot(data=data[data['id'] == '1514'].groupby(['point', 'id', 'player']).count().reset_index(), x='point', y='rank', hue='id', style='player', estimator=None).set(title='Point', xlabel='point', ylabel='count')
plt.savefig('1514_point_line.png')
plt.clf()
