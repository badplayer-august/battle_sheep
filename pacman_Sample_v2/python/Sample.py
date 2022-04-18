import random
import threading
import STcpClient
import time
import sys
import numpy as np
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

def getStep(playerStat, ghostStat, propsStat,otherPlayerStat,map):
    global action
    '''
    control of your player
    0: left, 1:right, 2: up, 3: down 4:no control
    format is (control, set landmine or not) = (0~3, True or False)
    put your control in action and time limit is 0.04sec for one step
    '''
    


    for prop in propsStat:
        x = int(prop[1]/25)
        y = int(prop[2]/25)
        if prop[0]==3:
            map[x][y]=-100 #active landmines,negative reward
        elif prop[0]==0:
            map[x][y]=100 #power pellets, positive reward
        elif prop[0]==1:
            map[x][y]=30 # landmines, positive reward
        elif prop[0]==2:
            map[x][y]=20 #pellets, reward
    for other in otherPlayerStat:
        x = int(other[0]/25)
        y = int(other[1]/25)
        if other[2] > 0:
            map[x][y]=-100 #other players have landmines, negative reward
        else:
            map[x][y]=-50 #other players do not have landmines,negative reward
    for ghost in ghostStat:
        x = int(ghost[0]/25)
        y = int(ghost[1]/25)
        map[x][y]=-100 # ghost, negative reward   
    landmine = False
    #move = random.choice([0, 1, 2, 3, 4])
    dirs = [[-1,0],[1,0],[0,1],[0,-1]] # move directions, left,right,up,down
    x = int(playerStat[0])
    y = int(playerStat[1])
    limit_x = max(int(playerStat[0]/25)+8,16)# define search space
    limit_y = max(int(playerStat[1]/25)+8,16)
    best_score = float("-inf")
    move=0
    global enemy 
    enemy = False # check if ghosts or players are aeound
    best_move=4
    for dir in dirs:
        score=[]
        visit = np.ones((17,17),dtype='int32')
        visit[int(playerStat[0]/25)][int(playerStat[1]/25)]=0
        x = int(playerStat[0]/25)+dir[0]
        y = int(playerStat[1]/25)+dir[1]
        search(map,x,y,limit_x,limit_y,visit,score)
        result = sum(score)
        #print(result)
        if result > best_score:
            best_move = move
            best_score = result
        move = move+1
    #print(map[int(playerStat[0]/25)][int(playerStat[1]/25)])
    #print(map[int(playerStat[0]/25)+dirs[best_move][0]][int(playerStat[1]/25)+dirs[best_move][1]])
    #if map[int(playerStat[0]/25)][int(playerStat[1]/25)]==0 or  map[int(playerStat[0]/25)+dirs[best_move][0]][int(playerStat[1]/25)+dirs[best_move][1]]==0:
    #    best_move = random.choice([0, 1, 2, 3, 4])
    #    print("here")
    if playerStat[2] > 0 and enemy==True:
        landmine = True
    action = [best_move, landmine]
def search(map,x,y,limit_x,limit_y,visit,score): # DFS
    if x>=17 or y>=17 or x<0 or y<0 or x>limit_x or y> limit_y or visit[x][y]==0 or map[x][y]==0:
        return
    visit[x][y]=0
    score.append(map[x][y])
    if map[x][y]==-100:
        enemy=True
    search(map,x+1,y,limit_x,limit_y,visit,score)
    search(map,x-1,y,limit_x,limit_y,visit,score)
    search(map,y+1,y,limit_x,limit_y,visit,score)
    search(map,y-1,y,limit_x,limit_y,visit,score)
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

    count=0
    while True:
        # playerStat: [x, y, n_landmine,super_time, score]
        # otherplayerStat: [x, y, n_landmine, super_time]
        # ghostStat: [[x, y],[x, y],[x, y],[x, y]]
        # propsStat: [[type, x, y] * N]
        map = np.ones((17,17),dtype='int32') #initialize map, 0 : wall, 1 : no wall
        parallel_wall = np.array(parallel_wall,dtype='int32')
        vertical_wall = np.array(vertical_wall,dtype='int32')
        for i in range(17):
            for j in range(16):
                if vertical_wall[i][j]==1:
                    map[i][j]=0
        for i in range(16):
            for j in range(17):
                if parallel_wall[i][j]==1:
                    map[i][j]=0
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
        
        user_thread = MyThread(target=getStep, args=(playerStat, ghostStat, propsStat,otherPlayerStat,map))
        user_thread.start()
        time.sleep(4/100)
        #print(action)
        if action == None:
            user_thread.kill()
            user_thread.join()
            action = [4, False]
        is_connect=STcpClient.SendStep(id_package, action[0], action[1])
        if not is_connect:
            break
