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
        self.myAnthillCoord = myAnthillCoord
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
            self.myFood = foods
            
            '''
            #find the food closest to the tunnel
            bestDistSoFar = 1000 #i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood = food
                    bestDistSoFar = dist
                    '''


        myQueen = myInv.getQueen()
        queenEmptyAdjacent = listAdjacent(myQueen.coords)
        queenEmptyAdjacent = [x for x in queenEmptyAdjacent if (getConstrAt(currentState, x) is None)]
        randomQueenEmptyAdjacent = queenEmptyAdjacent[random.randint(0, len(queenEmptyAdjacent) - 1)]
        
        #if the queen is on the anthill move her to a random adjacent empty place
        if (myQueen.coords == myInv.getAnthill().coords):
            if not myQueen.hasMoved:
                return Move(MOVE_ANT, [myInv.getQueen().coords, randomQueenEmptyAdjacent], None)
        '''
        # if the queen is on food and has not moved yet, move her
        if (myQueen.coords in getConstrList(currentState, None, (FOOD,))):
            if not myQueen.hasMoved:
                return Move(MOVE_ANT, [myInv.getQueen().coords, (1,0)], None)
                '''
        # if the queen is near the anthill and has not moved yet, move her
        if (myInv.getAnthill().coords in listAdjacent(myQueen.coords)):
            print "trying to move queen since she is by anthill"
            if (not myQueen.hasMoved):
                print "queen hasn't moved yet, so we are continuing"
                return Move(MOVE_ANT, [myInv.getQueen().coords, randomQueenEmptyAdjacent], None)

        #if the hasn't moved, have her move in place so she will attack
        if (not myQueen.hasMoved):
            print "queen hasn't moved yet, so move her in place"
            return Move(MOVE_ANT, [myQueen.coords], None)
            

        #determine if we need to build a soldier
        antlist = getAntList(currentState)
        #check for enemy soldiers / drones / ranged soldiers
        eSoldiers = 0
        eDrones = 0
        for ant in antlist:
            if (ant.player != me):
                if (ant.type == SOLDIER):
                    eSoldiers += 1
                elif (ant.type == R_SOLDIER):
                    eSoldiers += 1
                elif (ant.type == DRONE):
                    eDrones += 1
        #get anthill location
        anthill = myInv.getAnthill()
        #determine if we need to make a soldier
        # if (eSoldiers > len(getAntList(currentState, me, (SOLDIER,R_SOLDIER)))):
        if (True):
        #do we have enough food to build one?
            if (myInv.foodCount > 3):
                #move ant on hill out of the way if possible
                antOnHill = getAntAt(currentState, anthill.coords)
                if (antOnHill != None):
                    if (not antOnHill.hasMoved):
                        #randomly move ant out of the way
                        adjacentCoords = listReachableAdjacent(currentState, anthill.coords, \
                                                                       UNIT_STATS[antOnHill.type][MOVEMENT])
                        moveToCoords = adjacentCoords[random.randint(0, len(adjacentCoords) - 1)]
                        path = createPathToward(currentState, anthill.coords, moveToCoords, UNIT_STATS[antOnHill.type][MOVEMENT])
                        return Move(MOVE_ANT, path, None)
                #build soldier!
                else:
                    return Move(BUILD, [anthill.coords], SOLDIER)



        #build a drone if we need to
        if (eDrones > len(getAntList(currentState, me, [DRONE]))):
            print "trying to build a drone"
            #do we have enough food to build one?
            if (myInv.foodCount > 2):
                #move ant on hill out of the way if possible
                antOnHill = getAntAt(currentState, anthill.coords)
                if (antOnHill != None):
                    if (not antOnHill.hasMoved):
                        #randomly move ant out of the way
                        adjacentCoords = listReachableAdjacent(currentState, anthill.coords, \
                                                                   UNIT_STATS[antOnHill.type][MOVEMENT])
                        moveToCoords = adjacentCoords[random.randint(0, len(adjacentCoords) - 1)]
                        path = createPathToward(currentState, anthill.coords, moveToCoords, UNIT_STATS[antOnHill.type][MOVEMENT])
                        return Move(MOVE_ANT, path, None)
                #build drone!
                else:
                    return Move(BUILD, [anthill.coords], DRONE)

        #move soldiers towards anthill
        print "moving soldiers towards anthill"
        soldiers = getAntList(currentState, me, (SOLDIER, R_SOLDIER))
        for soldier in soldiers:
            if (not soldier.hasMoved):
                enemyAnts = []
                for ant in antlist:
                    if (ant.player != me):
                        enemyAnts.append(ant)
                #ants to attack
                workerTarget = None
                soldierTarget = None
                #look for ants to attack
                for ant in enemyAnts:
                    if (ant.type == WORKER):
                        workerTarget = ant.coords
                    if (ant.type == SOLDIER or ant.type == R_SOLDIER or ant.type == DRONE):
                        soldierTarget = ant.coords
                #try to attack fighting ants first, then workers, then anthill
                if (soldierTarget != None):
                    path = createPathToward(currentState, soldier.coords, soldierTarget, UNIT_STATS[SOLDIER][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
                elif (workerTarget != None):
                    path = createPathToward(currentState, soldier.coords, workerTarget, UNIT_STATS[SOLDIER][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
                else:
                    enemyAnthill = None
                    antHillList = getConstrList(currentState, None, [ANTHILL])
                    for anthill in antHillList:
                        if (anthill.player != me):
                            enemyAnthill = anthill
                    antOnHill = getAntAt(currentState, enemyAnthill.coords)
                    if (soldier.coords != enemyAnthill.coords):
                        path = createPathToward(currentState, soldier.coords, enemyAnthill.coords, UNIT_STATS[SOLDIER][MOVEMENT])
                        return Move(MOVE_ANT, path, None)


        #drones rush towards enemy anthill
        print "drones rush towards enemy anthill"
        drones = getAntList(currentState, me, (DRONE, ))
        for drone in drones:
            if (not drone.hasMoved):
                enemyAnthill = None
                antHillList = getConstrList(currentState, None, [ANTHILL])
                for anthill in antHillList:
                    if (anthill.player != me):
                        enemyAnthill = anthill
                antOnHill = getAntAt(currentState, enemyAnthill.coords)
                if (drone.coords != enemyAnthill.coords):
                    path = createPathToward(currentState, drone.coords, enemyAnthill.coords, UNIT_STATS[DRONE][MOVEMENT])
                    return Move(MOVE_ANT, path, None)




        #if I don't have two workers, and I have the food, build a worker
        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        print "numWorkers: " + str(numWorkers)
        if (numWorkers < 2):
            print "need to build more workers"
            if (myInv.foodCount > 0):
                return Move(BUILD, [myInv.getAnthill().coords], WORKER)

        


        myWorkers = getAntList(currentState, me, (WORKER,))
        print str(myWorkers)
        # move the workers
        for worker in myWorkers:
            if not worker.hasMoved:
                print "moving a worker"
                # if the worker has food and hasn't moved, move toward
                # the tunnel or anthill; whichever is closer
                if (worker.carrying):
                    workerTunnelDist = stepsToReach(currentState, worker.coords, self.myTunnel.coords)
                    workerAnthillDist = stepsToReach(currentState, worker.coords, self.myAnthillCoord)
                    
                    thingToMoveTowardCoord = (0,0)
                    if workerAnthillDist < workerTunnelDist:
                        thingToMoveTowardCoord = self.myAnthillCoord
                    else:
                        thingToMoveTowardCoord = self.myTunnel.coords
                    
                    path = createPathToward(currentState, worker.coords,
                                    thingToMoveTowardCoord, UNIT_STATS[WORKER][MOVEMENT])
                    return Move(MOVE_ANT, path, None)
                
                #if the worker has no food, move toward the nearest food
                else:
                    nearestFood = self.myFood[0]
                    nearestFoodDist = 1000 # infinity
                    for food in self.myFood:
                        newDist = stepsToReach(currentState, worker.coords, food.coords)
                        if newDist < nearestFoodDist:
                            nearestFoodDist = newDist
                            nearestFood = food
                    path = createPathToward(currentState, worker.coords,
                                            nearestFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                    return Move(MOVE_ANT, path, None)


        
        
        return Move(END, None, None)

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
