# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False): pass
    def update(self, state):    pass
    def pause(self):    pass
    def draw(self, state):    pass
    def updateDistributions(self, dist):    pass
    def finish(self):    pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0: allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules: inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        for index, inf in enumerate(self.inferenceModules):
            if not self.firstMove and self.elapseTimeEnable: 
                inf.elapseTime(gameState)
            self.firstMove = False
            if self.observeEnable:
                inf.observeState(gameState)
            self.ghostBeliefs[index] = inf.getBeliefDistribution()
        self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions

class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that
        has not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (in maze distance!).

        To find the maze distance between any two positions, use:
        self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
        successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief distributions
        for each of the ghosts that are still alive.  It is defined based
        on (these are implementation details about which you need not be
        concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.

        """
        # print "question 4"

        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = [beliefs for i,beliefs
                                            in enumerate(self.ghostBeliefs)
                                            if livingGhosts[i+1]]

        maxGhost = []
        for ghostProb in livingGhostPositionDistributions:
            currentMax = ghostProb.argMax()
            maxGhost.append(currentMax)
        index = 0
        goalPos = None
        maxDistance = 0
        for ghostPosition in maxGhost:
            probabity = livingGhostPositionDistributions[index][ghostPosition]
            if probabity>maxDistance:
                maxDistance = probabity
                goalPos = ghostPosition
            index+=1
        minDistance = 9999
        finalAction = None
        for action in legal:
            successorPosition = Actions.getSuccessor(pacmanPosition, action) # Next step for pacman
            newDistance = self.distancer.getDistance(successorPosition, goalPos)
            if newDistance < minDistance:
                minDistance = newDistance
                finalAction = action
        return finalAction



            # index, prob = livingGhostPositionDistributions.max(axis=0)
            # print "index: ", index
            # print "prob: ", prob
        # maxGhost = livingGhostPositionDistributions.

        # print "localMax", localMax
        #     localMax [(7, 3), (7, 6), (12, 3), (14, 6)]

        # print "legal: ", legal
        #     legal:  ['Stop', 'East', 'South']
        # print "livingGhosts: ", livingGhosts
        #     livingGhosts:  [False, True, True, True, True]
        # print "livingGhostPositionDistributions: ", livingGhostPositionDistributions  
        #     livingGhostPositionDistributions:  [{(7, 3): 0.10829103214890017, (1, 3): 0.001692047377326565, (6, 6): 0.00676818950930626, (5, 6): 0.00338409475465313, (14, 4): 0.001692047377326565                                  
        # "*** YOUR CODE HERE ***"
        # util.raiseNotDefined()