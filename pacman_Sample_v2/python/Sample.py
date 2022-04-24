import random
from secrets import choice
import threading
import STcpClient
import time
import sys
import numpy as np
import copy
class MyThread(threading.Thread): 
   def __init__(self, *args, **keywords): 
       threading.Thread.__init__(self, *args, **keywords) 
       self.killed = False      
   def start(self):         
       self.__run_backup = self.run         
       self.run = self.__run                
       threading.Thread.start(self)         
   def __run(self):         
       sys.settrace(self.globaltrace)         
       self.__run_backup()         
       self.run = self.__run_backup         
   def globaltrace(self, frame, event, arg):         
       if event == 'call':             
           return self.localtrace         
       else:             
           return None        
   def localtrace(self, frame, event, arg):         
       if self.killed:             
          if event == 'line':                 
              raise SystemExit()         
       return self.localtrace         
   def kill(self):         
       self.killed = True
pre_move = -100
pre_x = -1
pre_y = -1
def getStep(playerStat, ghostStat, propsStat,otherPlayerStat,right_map,left_map,up_map,down_map):
    global action
    global pre_move
    global pre_x
    global pre_y
    bomb = False
    if playerStat[2] > 0:
        bomb = True
    '''
    control of your player
    0: left, 1:right, 2: up, 3: down 4:no control
    format is (control, set landmine or not) = (0~3, True or False)
    put your control in action and time limit is 0.04sec for one step
    '''
    dirs = [[0,-1],[0,1],[-1,0],[1,0]]
    reward_map=np.zeros((16,16),dtype='int32')
    maze_wall=[left_map,right_map,up_map,down_map]
    for prop in propsStat:
        x = int(prop[1]/25)
        y = int(prop[2]/25)
        if prop[0]==3:
            reward_map[x][y]=-100 #active landmines,negative reward
        elif prop[0]==0:
            reward_map[x][y]=100 #power pellets, positive reward
        elif prop[0]==1:
            reward_map[x][y]=100 # landmines, positive reward
        elif prop[0]==2:
            reward_map[x][y]=50 #pellets, reward
    for other in otherPlayerStat:
        x = int(other[0]/25)
        y = int(other[1]/25)
        if other[2] > 0:
            reward_map[x][y]=-100 #other players have landmines, negative reward
    for ghost in ghostStat:
        x = int(ghost[0]/25)
        y = int(ghost[1]/25)
        reward_map[x][y]=-100 # ghost, negative reward   
    best_reward = -1000
    best_move=4
    x = int(playerStat[0]/25)
    y = int(playerStat[1]/25)
    if pre_x==x and pre_y==y:
        best_move=random.choice([0,1,2,3])
        action = [best_move,bomb]
        pre_move = best_move
        return       
    #print("x: ",x)
    #print("y: ",y)
    #print("pre move:",pre_move)
    if pre_move !=-100:
        dir=[]
        if pre_move%2==1:
            banned=pre_move-1
        else:
            banned=pre_move+1
        for i in range(4):
            if i != banned:
                dir.append(i)
        for d in dir:
             wall = maze_wall[d]
             
             if wall[x][y]==1:
                reward = copy.deepcopy(reward_map[x][y])
                #print("d: ",d)
                #print("maze: ",wall[x][y])
                if reward >best_reward:
                    best_move=copy.deepcopy(d)
                    best_reward=copy.deepcopy(reward)           
    else:
        for i in range(4):
            wall = maze_wall[i]
            if wall[x][y]==1:
                reward = copy.deepcopy(reward_map[x][y])
                #print(wall[x][y])
                if reward >best_reward:
                    best_move=copy.deepcopy(i)
                    best_reward=copy.deepcopy(reward)
    pre_move = best_move
    action =[best_move,bomb]    
    pre_x = int(playerStat[0]/25)
    pre_y = int(playerStat[1]/25)
    #global enemy 
    #enemy = False # check if ghosts or players are aeound
    
    
    #if playerStat[2] > 0 and enemy==True:
    #    landmine = True
    #action = [best_move, landmine]
    
def search(x,y,limit_max_x,limit_max_y,limit_min_x,limit_min_y,visit,score,reward_map,left_map,right_map,up_map,down_map): # DFS
    if x>=16 or x<0 or y>=16 or y<0 or visit[x][y]==0:
        return
    visit[x][y]=0
    score.append(reward_map[x][y])
    if reward_map[x][y]==-100:
        enemy=True
    if  x+1<=limit_max_x and down_map[x][y]==1:
        search(x+1,y,limit_max_x,limit_max_y,limit_min_x,limit_min_y,visit,score,reward_map,left_map,right_map,up_map,down_map)
    if  x-1>=limit_min_x and up_map[x][y]==1:
        search(x-1,y,limit_max_x,limit_max_y,limit_min_x,limit_min_y,visit,score,reward_map,left_map,right_map,up_map,down_map)

    if  y+1<=limit_max_y and  right_map[x][y]==1:
        search(y+1,y,limit_max_x,limit_max_y,limit_min_x,limit_min_y,visit,score,reward_map,left_map,right_map,up_map,down_map)

    if  y-1>=limit_min_y and left_map[x][y]==1:
        search(y-1,y,limit_max_x,limit_max_y,limit_min_x,limit_min_y,visit,score,reward_map,left_map,right_map,up_map,down_map)
# props img size => pellet = 5*5, landmine = 11*11, bomb = 11*11
# player, ghost img size=23x23


if __name__ == "__main__":
    # parallel_wall = zeros([16, 17])
    # vertical_wall = zeros([17, 16])
    (stop_program, id_package, parallel_wall, vertical_wall) = STcpClient.GetMap()

    #print("parallel wall")
    #print(np.array(parallel_wall,dtype='int32').T)
    #print("vertical wall")
    #print(np.array(vertical_wall,dtype='int32').T)
    #count=0
    parallel_wall = np.array(parallel_wall,dtype='int32').T
    vertical_wall = np.array(vertical_wall,dtype='int32').T

    left_map = np.ones((16,16),dtype='int32')
    right_map = np.ones((16,16),dtype='int32')
    up_map = np.ones((16,16),dtype='int32')
    down_map = np.ones((16,16),dtype='int32')
    for i in range(16):
        for j in range(16):
            if parallel_wall[i][j]==1:
                up_map[i][j]=0
            if vertical_wall[i][j]==1:
                left_map[i][j]=0
    for i in range(16):
        for j in range(1,17):
            if vertical_wall[i][j]==1:
                right_map[i][j-1]=0
    for i in range(1,17):
        for j in range(16):
            if parallel_wall[i][j]==1:
                down_map[i-1][j]=0
    print("LEFT_wall")
    print(left_map)  
    print("right_wall")
    print(right_map) 
    print("up_wall")
    print(up_map)  
    print("down_wall")
    print(down_map) 
    while True:
        
        # playerStat: [x, y, n_landmine,super_time, score]
        # otherplayerStat: [x, y, n_landmine, super_time]
        # ghostStat: [[x, y],[x, y],[x, y],[x, y]]
        # propsStat: [[type, x, y] * N]
        #map = np.ones((17,17),dtype='int32') #initialize map, 0 : wall, 1 : no wall

        (stop_program, id_package, playerStat,otherPlayerStat, ghostStat, propsStat) = STcpClient.GetGameStat()
        #if count == 0:
            #print("ghostState: ")
            #print(ghostStat)
            #print("otherPlayerState: ")
            #print(otherPlayerStat)
            #count+=1
        #print("propsState: ")
        #print(propsStat)
        if stop_program:
            break
        elif stop_program is None:
            break
        global action
        action = None
        
        user_thread = MyThread(target=getStep, args=(playerStat, ghostStat, propsStat,otherPlayerStat,right_map,left_map,up_map,down_map))
        user_thread.start()
        #print(action)
        time.sleep(4/100)
        #print(action)
        #move = random.choice([0, 1, 2, 3, 4])
        #move = test[i]
        #print("x: ",playerStat[0])
        #print("y: ",playerStat[1])
        #action = [move,False]
        
        print(action)
        if action == None:
            user_thread.kill()
            user_thread.join()
            action = [4, False]
        is_connect=STcpClient.SendStep(id_package, action[0], action[1])
        if not is_connect:
            break
