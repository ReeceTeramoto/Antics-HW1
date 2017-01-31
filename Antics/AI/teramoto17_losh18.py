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
import time

#Debug output
VERBOSE = False

# moves ant to a random empty adjacent square
def moveAntToRandEmptyAdj(currentState, ant):
    "move random empty adjacent"
    adjacentCoords = listReachableAdjacent(currentState, ant.coords, \
                                           UNIT_STATS[ant.type][MOVEMENT])
    if (len(adjacentCoords) == 0): #if we can't move, stay in the same spot (duh?)
        adjacentCoords = [ant.coords]
    moveToCoords = adjacentCoords[random.randint(0, len(adjacentCoords) - 1)]
    path = createPathToward(currentState, ant.coords, moveToCoords, UNIT_STATS[ant.type][MOVEMENT])
    return Move(MOVE_ANT, path, None)

#
# Handles queen movement
#
def moveQueen(myQueen, myInv, currentState):

    foods = getConstrList(currentState, None, (FOOD,))
    #if the queen is on the anthill move her to a random adjacent empty place
    if (myQueen.coords == myInv.getAnthill().coords):
        if not myQueen.hasMoved:
            return moveAntToRandEmptyAdj(currentState, myQueen)

    #move queen off of food
    for food in foods:
        if (myQueen.coords == food.coords):
            if not myQueen.hasMoved:
                return moveAntToRandEmptyAdj(currentState, myQueen)
        
    # if the queen is on food and has not moved yet, move her
    if (myQueen.coords in getConstrList(currentState, None, (FOOD,))):
        if not myQueen.hasMoved:
            moveAntToRandEmptyAdj(currentState, myQueen)
    # if the queen is near the anthill and has not moved yet, move her
    if (myInv.getAnthill().coords in listAdjacent(myQueen.coords)):
        if (VERBOSE): print "trying to move queen since she is by anthill"
        if (not myQueen.hasMoved):
            if (VERBOSE): print "queen hasn't moved yet, so we are continuing"
            return moveAntToRandEmptyAdj(currentState, myQueen)

    #if the hasn't moved, have her move in place so she will attack
    if (not myQueen.hasMoved):
        if (VERBOSE): print "queen hasn't moved yet, so move her in place"
        return Move(MOVE_ANT, [myQueen.coords], None)

#
# Handles worker movement
#
def moveWorker(worker, currentState, self):
    if (VERBOSE): print "moving a worker"
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
        if (len(path) == 1): #stuck on something
            #randomly move ant out of the way
            return moveAntToRandEmptyAdj(currentState, worker)
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
        #stuck on something, move randomly to escape
        if (len(path) == 1): #stuck on something
            #randomly move ant out of the way
            return moveAntToRandEmptyAdj(currentState, worker)
        return Move(MOVE_ANT, path, None)


#Build a soldier
#Arguments: currentState: current game state
#           myInv: current inventory
#Returns: Build move if soldier can be built, or
#         Move ant off of anthill if blocking, or
#         None if cannot build currently (anthill is blocked)
def buildSoldier(currentState, myInv):
    anthill = myInv.getAnthill()
    #move ant on hill out of the way if possible
    antOnHill = getAntAt(currentState, anthill.coords)
    if (antOnHill != None):
        if (not antOnHill.hasMoved):
            #randomly move ant out of the way
            return moveAntToRandEmptyAdj(currentState, antOnHill)
        else:
            return None
    #build soldier!
    else:
        return Move(BUILD, [anthill.coords], SOLDIER)


#Builds a drone
#Arguments: currentState current game state, myInv: current player's inventory
#Returns: Build move to build drone, or move ant off of the anthill
def buildDrone(currentState, myInv):
    anthill = myInv.getAnthill()
    myInv = getCurrPlayerInventory(currentState)
    if (VERBOSE): print "trying to build a drone"
    #do we have enough food to build one?
    if (myInv.foodCount > 2):
        #move ant on hill out of the way if possible
        antOnHill = getAntAt(currentState, anthill.coords)
        if (antOnHill != None):
            if (not antOnHill.hasMoved):
                #randomly move ant out of the way
                return moveAntToRandEmptyAdj(currentState, antOnHill)
        #build drone!
        else:
            return Move(BUILD, [anthill.coords], DRONE)

# Moves a soldier ant
#Arguments: currentState current game state
#           soldier: soldier ant to move
#Returns: Move object to move soldier ant
def moveSoldier(currentState, soldier):
    me = currentState.whoseTurn
    antlist = getAntList(currentState)
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

#Moves a drone ant towards the enemy anthill
#Arugments: currentState: current game state
#           drone: drone to move
#Returns: Move object for moving drone towards anthill
def moveDrone(currentState, drone):
    me = currentState.whoseTurn
    enemyAnthill = None
    antHillList = getConstrList(currentState, None, [ANTHILL])
    for anthill in antHillList:
        if (anthill.player != me):
            enemyAnthill = anthill
    antOnHill = getAntAt(currentState, enemyAnthill.coords)
    if (drone.coords != enemyAnthill.coords):
        path = createPathToward(currentState, drone.coords, enemyAnthill.coords, UNIT_STATS[DRONE][MOVEMENT])
        return Move(MOVE_ANT, path, None)

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
        super(AIPlayer,self).__init__(inputPlayerId, "HW1 Teramoto-Losh")
    
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
            if (VERBOSE): print "anthill coords: " + str(anthillCoords)
            for elem in anthillCoords:
                if elem != myAnthillCoord:
                    enemyAnthillCoord = elem
            if (VERBOSE): print "enemy anthill coord: " + str(enemyAnthillCoord)
            
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
        anthill = myInv.getAnthill()
        
        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myTunnel is None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood is None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods
        
        # move the queen if she hasn't moved yet
        myQueen = myInv.getQueen()
        if not myQueen.hasMoved:
            return moveQueen(myQueen, myInv, currentState)
    
        #determine if we need to build a soldier or drone
        antlist = getAntList(currentState, None, (DRONE,))
        #check for enemy drones (this responds to rushes)
        enemyDrones = len([drone for drone in antlist if (drone.player != me)])
        if (VERBOSE): print "Enemy Drones: " + str(enemyDrones)
        
        #do we have enough food to build a soldier? If so, build one.
        if (myInv.foodCount > 3):
            returnMove = buildSoldier(currentState, myInv)
            if not (returnMove is None): #make sure that we can build a soldier
                return returnMove

        #build a drone if we need to (respond to enemy drone rush)
        if (enemyDrones > len(getAntList(currentState, me, [DRONE]))):
            returnMove = buildDrone(currentState, myInv)
            if not (returnMove is None): #make sure that we can build a drone
                return returnMove

        #move soldiers towards enemy ants and anthill
        if (VERBOSE): print "moving soldiers"
        soldiers = getAntList(currentState, me, (SOLDIER, R_SOLDIER))
        for soldier in soldiers:
            if (not soldier.hasMoved):
                returnMove = moveSoldier(currentState, soldier)
                if not (returnMove is None):
                    return returnMove

        #drones rush towards enemy anthill
        if (VERBOSE): print "moving drones"
        drones = getAntList(currentState, me, (DRONE, ))
        for drone in drones:
            if (not drone.hasMoved):
                returnMove = moveDrone(currentState, drone)
                if not (returnMove is None):
                    return returnMove

        #if I don't have two workers, and I have the food, build a worker
        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        if (VERBOSE): print "numWorkers: " + str(numWorkers)
        if (numWorkers < 2):
            if (VERBOSE): print "need to build more workers"
            if (myInv.foodCount > 0):
                if (getAntAt(currentState, anthill.coords) is None):
                    return Move(BUILD, [myInv.getAnthill().coords], WORKER)

        # get all workers
        myWorkers = getAntList(currentState, me, (WORKER,))
        if (VERBOSE): print str(myWorkers)
        #shuffle worker
        random.shuffle(myWorkers)
        # move the workers
        for worker in myWorkers:
            if not worker.hasMoved:
                
                return moveWorker(worker, currentState, self)

        
        return Move(END, None, None)
                    
    ##
    #getAttack
    #
    # Attack the first enemy seen
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
