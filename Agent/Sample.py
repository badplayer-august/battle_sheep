import MCTS_Battle_Sheep
import STcpClient
import numpy as np
import random

'''
    選擇起始位置
    選擇範圍僅限場地邊緣(至少一個方向為牆)
    
    return: init_pos
    init_pos=[x,y],代表起始位置
    
'''


def InitPos(mapStat):
    mapStat = np.array(mapStat)
    sheepStat = np.zeros((12, 12))
    sheepStat[mapStat != 0] = 16
    sheepStat = list(sheepStat)
    playerID = 1
    while (mapStat == playerID).any():
        playerID += 1
    
    action = MCTS(MCTS_NODE(BattleSheepState(mapStat, sheepStat, playerID))).best_action(1000, c_param=1.4, h=10)
    return [action.i, action.j]


'''
    產出指令
    
    input: 
    playerID: 你在此局遊戲中的角色(1~4)
    mapStat : 棋盤狀態(list of list), 為 12*12矩陣, 
              0=可移動區域, -1=障礙, 1~4為玩家1~4佔領區域
    sheepStat : 羊群分布狀態, 範圍在0~16, 為 12*12矩陣

    return Step
    Step : 3 elements, [(x,y), m, dir]
            x, y 表示要進行動作的座標 
            m = 要切割成第二群的羊群數量
            dir = 移動方向(1~6),對應方向如下圖所示
              1  2
            3  x  4
              5  6
'''
def GetStep(playerID, mapStat, sheepStat):
    action = MCTS(MCTS_NODE(BattleSheepState(np.array(mapStat), list(sheepStat), playerID))).best_action(1000, c_param=1.4, h=10)
    return [(action.i, action.j), action.m, action.d]


# player initial
(id_package, playerID, mapStat) = STcpClient.GetMap()
init_pos = InitPos(mapStat)
STcpClient.SendInitPos(id_package, init_pos)

# start game
while (True):
    (end_program, id_package, mapStat, sheepStat) = STcpClient.GetBoard()
    if end_program:
        STcpClient._StopConnect()
        break
    Step = GetStep(playerID, mapStat, sheepStat)

    STcpClient.SendStep(id_package, Step)
