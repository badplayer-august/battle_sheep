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
    
    #print("super time:", playerStat[3])
    if playerStat[3] > 0:
        super_time=10
    else:
        super_time=-1
    '''
    control of your player
    0: left, 1:right, 2: up, 3: down 4:no control
    format is (control, set landmine or not) = (0~3, True or False)
    put your control in action and time limit is 0.04sec for one step
    '''
    reward_map=np.zeros((16,16),dtype='int32')
    maze_wall=[left_map,right_map,up_map,down_map]
    for prop in propsStat:
        x = int(prop[1]/25)
        y = int(prop[2]/25)
        if prop[0]==3:
            reward_map[x][y]+=-100 #active landmines,negative reward
            for i in range(16):
                reward_map[i][y]+=-50*(16-abs(x-i))
                reward_map[x][i]+=-50*(16-abs(y-i))
            
        elif prop[0]==0:
            reward_map[x][y]+=10000 #power pellets, positive reward
            for i in range(16):
                reward_map[i][y]+=5000*(16-abs(x-i))
                reward_map[x][i]+=5000*(16-abs(y-i))            
        elif prop[0]==1:
            reward_map[x][y]+=100 # landmines, positive reward
            for i in range(16):
                reward_map[i][y]+=50*(16-abs(x-i))
                reward_map[x][i]+=50*(16-abs(y-i))          
        elif prop[0]==2:
            reward_map[x][y]+=500 #pellets, reward
            for i in range(16):
                reward_map[i][y]+=300*(16-abs(x-i))
                reward_map[x][i]+=300*(16-abs(y-i))             
    for other in otherPlayerStat:
        x = int(other[0]/25)
        y = int(other[1]/25)
        if other[2] > 0:
            reward_map[x][y]+=-100 #other players have landmines, negative reward
    for ghost in ghostStat:
        x = int(ghost[0]/25)
        y = int(ghost[1]/25)
        reward_map[x][y]+=super_time*100 # ghost, negative reward
        for i in range(16):
            reward_map[i][y]+=super_time*100*(16-abs(x-i))
            reward_map[x][i]+=super_time*100*(16-abs(y-i))                
    best_reward = float("-inf")
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
    way = [[-1,0],[1,0],[0,-1],[0,1]]
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
                if x+way[d][0]>=0 and y+way[d][1]>=0 and x+way[d][0]<=15 and y+way[d][1]<=15:
                    reward = copy.deepcopy(reward_map[x+way[d][0]][y+way[d][1]])
                    if reward <500 and playerStat[2] > 0:
                        bomb=True
                    #print("d: ",d)
                    #print("maze: ",wall[x][y])
                    if reward >=best_reward:
                        best_move=copy.deepcopy(d)
                        #best_move_choice.append(d)
                        best_reward=copy.deepcopy(reward)       
    else:
        for i in range(4):
            wall = maze_wall[i]
            if wall[x][y]==1:
                if x+way[i][0]>=0 and y+way[i][1]>=0 and x+way[i][0]<=15 and y+way[i][1]<=15:
                    reward = copy.deepcopy(reward_map[x+way[i][0]][y+way[i][0]])
                    #print(wall[x][y])
                    if reward >=best_reward:
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
