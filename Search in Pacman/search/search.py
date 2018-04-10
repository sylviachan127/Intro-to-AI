# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
from multiprocessing.managers import State
from matplotlib.pyplot import step


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
import pacman

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    print "I am here!!!"
    return  [s, s, w, s, w, w, s, w]

def dFSbFS(problem, s):
    visited = []
    s.push((problem.getStartState(),[]));
    while not s.isEmpty():
        coord, dir = s.pop();
        if not (coord in visited):
            visited.append(coord)
            if problem.isGoalState(coord):
                return dir
            for state, direction, step in problem.getSuccessors(coord):
                s.push((state, dir+[direction]))
    util.raiseNotDefined()
    return [];

def depthFirstSearch(problem):
    return dFSbFS(problem, util.Stack())
def breadthFirstSearch(problem):
    return dFSbFS(problem, util.Queue())

def initial(problem):
    print "Start:", problem.getStartState() #(34, 16)
    print "Is the start a goal?", problem.isGoalState(problem.getStartState()) #False
    print "Start's successors:", problem.getSuccessors(problem.getStartState()) #[((34, 15), 'South', 1), ((33, 16), 'West', 1)]
                
def uniformCostSearch(problem):
    visited = []
    solution = []
    intialCost = 0
    priorityQueue = util.PriorityQueue()
    priorityQueue.push((problem.getStartState(),solution,intialCost),intialCost)
    
    while not priorityQueue.isEmpty():
        coord, solution, totalStep = priorityQueue.pop()
        if problem.isGoalState(coord):
            return solution
        if not coord in visited:
            visited+=[coord]
            for position, direction, step in problem.getSuccessors(coord):
                newSolution = solution+[direction]
                newTotalCost = totalStep+step
                priorityQueue.push((position,newSolution,newTotalCost),newTotalCost)
            
def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0
                
def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    visited = []
    solution = []
    intialCost = 0
    priorityQueue = util.PriorityQueue()
    priorityQueue.push((problem.getStartState(),solution,intialCost),intialCost)
     
    while not priorityQueue.isEmpty():
        coord, solution, totalStep = priorityQueue.pop()
        if problem.isGoalState(coord):
            return solution
        if not coord in visited:
            visited+=[coord]
            for position, direction, step in problem.getSuccessors(coord):
                newSolution = solution+[direction]
                g = totalStep + step
                newTotalCost = g + heuristic(position, problem)
                priorityQueue.push((position, newSolution, g), newTotalCost)

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
