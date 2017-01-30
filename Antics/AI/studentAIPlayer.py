  # -*- coding: latin-1 -*-
import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "HW1 AI Player")
    
    ##
    #getPlacement
    #
    #Description: The getPlacement method corresponds to the 
    #action taken on setup phase 1 and setup phase 2 of the game. 
    #In setup phase 1, the AI player will be passed a copy of the 
    #state as currentState which contains the board, accessed via 
    #currentState.board. The player will then return a list of 11 tuple 
    #coordinates (from their side of the board) that represent Locations 
    #to place the anthill and 9 grass pieces. In setup phase 2, the player 
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent's side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to 
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of eleven 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    ### Anthill in corner, tunnel at other corner, grass forming a line on the border
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None
        
        myAnthillCoord = (0, 0)
        myTunnelCoord = (9, 0)
        
        if currentState.phase == SETUP_PHASE_1:
            
            
            
            return [myAnthillCoord, (9, 0),
                    (0,3), (1,3), (2,3), (3,3), \
                    (4,3), (5,3), (6,3), \
                    (7,3), (8,3) ];
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []
            
            # find the 2 most furthest empty spots from the enemy's anthill
            
            # find enemy's anthill
            enemyAnthillCoord = (15, 15)
            anthillCoords = [x.coords for x in getConstrList(currentState, None, (ANTHILL,))]
            # enemy's anthill is the one that is no my anthill's coordinates
            print "anthill coords: " + str(anthillCoords)
            for elem in anthillCoords:
                if elem != myAnthillCoord:
                    enemyAnthillCoord = elem
            print "enemy anthill coord: " + str(enemyAnthillCoord)
            
            # find 2 furthest empty spots from enemy's anthill
            allEmptySpots = []
            for x in range(0, 10):
                for y in range(6, 10):
                    spot = (x,y)
                    # if the spot is empty, get its distance
                    distance = stepsToReach(currentState, enemyAnthillCoord, spot)
                    if getConstrAt(currentState, spot) is None:
                        allEmptySpots.append([distance, spot])
            # sort all empty spots by distance
            allEmptySpots = sorted(allEmptySpots, reverse = True)
            
            # get the 2 furthest spots from enemy's anthill
            foodPos1 = allEmptySpots[0][1]
            foodPos2 = allEmptySpots[1][1]
            
            # place the food at these 2 spots
            moves.append(foodPos1)
            moves.append(foodPos2)
            return moves
            
        else:
            return None  #should never happen

    ##
    #getMove
    #
    #
    #
    ##
    def getMove(self, currentState):
        #Useful pointers
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn
        
        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood == None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            #find the food closest to the tunnel
            bestDistSoFar = 1000 #i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood = food
                    bestDistSoFar = dist



        #if all of my workers have moved, we're done
        myWorkers = getAntList(currentState, me, (WORKER,))
        allWorkersMoved = True
        for worker in myWorkers:
            if not (worker.hasMoved):
                allWorkersMoved = False
        if allWorkersMoved:
            return Move(END, None, None)

        #if the queen is on the anthill move her
        myQueen = myInv.getQueen()
        if (myQueen.coords == myInv.getAnthill().coords):
            return Move(MOVE_ANT, [myInv.getQueen().coords, (1,0)], None)

        #if the hasn't moved, have her move in place so she will attack
        if (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)
            
        #if I have the food and the anthill is unoccupied then
        #make a drone
        if (myInv.foodCount > 2):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], DRONE)

        #Move all my drones towards the enemy
        myDrones = getAntList(currentState, me, (DRONE,))
        for drone in myDrones:
            if not (drone.hasMoved):
                droneX = drone.coords[0]
                droneY = drone.coords[1]
                if (droneY < 9):
                    droneY += 1;
                else:
                    droneX += 1;
                if (droneX,droneY) in listReachableAdjacent(currentState, drone.coords, 3):
                    return Move(MOVE_ANT, [drone.coords, (droneX, droneY)], None)
                else:
                    return Move(MOVE_ANT, [drone.coords], None)

        #for each worker, if the worker has food, move toward tunnel
        for worker in myWorkers:
            if (worker.carrying):
                path = createPathToward(currentState, worker.coords,
                                    self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, path, None)
                    
            #if the worker has no food, move toward food
            else:
                path = createPathToward(currentState, worker.coords,
                                        self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, path, None)

        #if I don't have two workers, and I have the food, build a worker
        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        print "numWorkers: " + str(numWorkers)
        if (numWorkers < 2):
            if (myInv.foodCount > 0):
                return Move(BUILD, [myInv.getAnthill().coords], WORKER)

    ##
    #getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  #don't care

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
