import pygame, os, random, time, pickle
import tensorflow as tf
import numpy as np
from enum import Enum
from pygame.locals import *

class Cell:
    def __init__(self, row, column):
        self.row = row
        self.column = column

class Mode(Enum):
    PVP = 1
    PVB = 2
    BVB = 3

#class Bot():
#    __init__()

mode = Mode.PVP

dir = os.path.dirname(__file__)

boardPathRel = "Resources\TicTacToeBoard.jpg"
oPathRel = "Resources\O.png"
xPathRel = "Resources\X.png"
boardPath = os.path.join(dir, boardPathRel)
oPath = os.path.join(dir, oPathRel)
xPath = os.path.join(dir, xPathRel)

black = (0,0,0)
white = (255,255,255)
green = (0, 255, 0)

tWidth = 1020
tHeight = 1020
width = 300
height = 300
margin = 50
bar = 10
grid = []
for row in range(3):
    grid.append([])
    for column in range(3):
        grid[row].append(0)

turn = 1
sTurn = 1
oWins = 0
xWins = 0
draws = 0

realTime = True
smartResult = False
displayGame = True

REWARD_WIN = 1
REWARD_DRAW = 0.5
REWARD_LOSE = -1

gamma = 0.8
run_name = "%s" % int(time.time())

exp_rate_initial = 1.0
exp_rate_final = .01
epochs = 5000
currentEpoch = 1
learning_rate = .001

episode_max = 10000
episode_stats = 100

oBoard = pickle.load(open(os.path.join(dir, 'data/oBoard.pkl'), 'rb'))
oBoardFinal = pickle.load(open(os.path.join(dir, 'data/oBoardFinal.pkl'), 'rb'))
oChoices = []
xBoard = pickle.load(open(os.path.join(dir, 'data/xBoard.pkl'), 'rb'))
oBoardFinal = pickle.load(open(os.path.join(dir, 'data/oBoardFinal.pkl'), 'rb'))
xChoices = []
print(oBoard[0])
#Formatting data files
'''
oBoard = []
xBoard = []
for sTurnNum in range(2):
    oBoard.append([sTurnNum+1])
    for gen in range(epochs):
        oBoard[sTurnNum].append([gen+1])
for sTurnNum in range(2):
    xBoard.append([sTurnNum+1])
    for gen in range(epochs):
        xBoard[sTurnNum].append([gen+1])

pickle.dump(oBoard, open(os.path.join(dir, 'data/oBoard.pkl'), 'wb'))
pickle.dump(xBoard, open(os.path.join(dir, 'data/xBoard.pkl'), 'wb'))
'''

pygame.init()
pygame.font.init()
pygame.display.set_caption('TicTacToe')

gameDisplay = pygame.display.set_mode((tWidth, tHeight))
screen = pygame.display.get_surface()
clock = pygame.time.Clock()

board = pygame.image.load(boardPath)
oImg = pygame.image.load(oPath)
xImg = pygame.image.load(xPath)
font = pygame.font.SysFont('Comic Sans MS', 30)

crashed = False

def saveFiles():
    pickle.dump(oBoard, open(os.path.join(dir, 'data/oBoardSmart.pkl'), 'wb'))
    pickle.dump(xBoard, open(os.path.join(dir, 'data/xBoardSmart.pkl'), 'wb'))

def isWinner(bo, x):
    return ((bo[0][0] == x and bo[0][1] == x and bo[0][2] == x) or
    (bo[1][0] == x and bo[1][1] == x and bo[1][2] == x) or
    (bo[2][0] == x and bo[2][1] == x and bo[2][2] == x) or
    (bo[0][0] == x and bo[1][0] == x and bo[2][0] == x) or
    (bo[0][1] == x and bo[1][1] == x and bo[2][1] == x) or
    (bo[0][2] == x and bo[1][2] == x and bo[2][2] == x) or
    (bo[0][0] == x and bo[1][1] == x and bo[2][2] == x) or
    (bo[0][2] == x and bo[1][1] == x and bo[2][0] == x))

def isDraw(bo):
    for row in range(3):
        for column in range(3):
            if(bo[row][column]==0):
                return False
    return True

def flattenBoard(board, row, column):
    if row == 0 and column == 0:
        board.extend([1])
        return board
    elif row == 0 and column == 1:
        board.extend([2])
        return board
    elif row == 0 and column == 2:
        board.extend([3])
        return board
    elif row == 1 and column == 0:
        board.extend([4])
        return board
    elif row == 1 and column == 1:
        board.extend([5])
        return board
    elif row == 1 and column == 2:
        board.extend([6])
        return board
    elif row == 2 and column == 0:
        board.extend([7])
        return board
    elif row == 2 and column == 1:
        board.extend([8])
        return board
    elif row == 2 and column == 2:
        board.extend([9])
        return board

def unFlattenBoard(item):
    if item == 1:
        row = 0
        column = 0
        return Cell(row, column)
    elif item == 2:
        row = 0
        column = 1
        return Cell(row, column)
    elif item == 3:
        row = 0
        column = 2
        return Cell(row, column)
    elif item == 4:
        row = 1
        column = 0
        return Cell(row, column)
    elif item == 5:
        row = 1
        column = 1
        return Cell(row, column)
    elif item == 6:
        row = 1
        column = 2
        return Cell(row, column)
    elif item == 7:
        row = 2
        column = 0
        return Cell(row, column)
    elif item == 8:
        row = 2
        column = 1
        return Cell(row, column)
    elif item == 9:
        row = 2
        column = 2
        return Cell(row, column)

def updateChoices(winner):
    global mode, currentEpoch, oChoices, xChoices, sTurn
    if winner == "o":
        oChoices.extend([REWARD_WIN])
        xChoices.extend([REWARD_LOSE])
    elif winner == "x":
        oChoices.extend([REWARD_LOSE])
        xChoices.extend([REWARD_WIN])
    elif winner == "draw":
        oChoices.extend([REWARD_DRAW])
        xChoices.extend([REWARD_DRAW])
    oBoard[sTurn-1][currentEpoch].append(oChoices)
    xBoard[sTurn-1][currentEpoch].append(xChoices)
    print(oBoard[sTurn-1][currentEpoch][1])
    oChoices = []
    xChoices = []
    currentEpoch+=1

def resetBoard(winner):
    global grid, mode, currentEpoch, oChoices, xChoices, sTurn
    del grid
    grid = []
    for row in range(3):
        grid.append([])
        for column in range(3):
            grid[row].append(0)
    print(currentEpoch)
    if mode == Mode.PVB or mode == Mode.BVB:
        updateChoices(winner)

def determineBestCell(boardResults, curEpoch, rewardBoard, move):
    global oBoard
    pastResults = []
    for st in range(2):
        for gen in range(curEpoch):
            for x in range(9):
                print(oBoard[st][gen])
                if x+1 in boardResults and x+1 == rewardBoard[st][gen][1][move]:
                    cell = x+1
                    value = int(rewardBoard[st][gen][1][-1])
                    pastResults.extend([cell, value])


def randomlySelectCell(origBoard, letter):
    global oChoices, xChoices
    board = []
    for row in range(3):
        for column in range(3):
            if origBoard[row][column] == 0:
                board = flattenBoard(board,row,column)
    #print(board)
    choice = random.choice(board)
    if letter == "o":
        oChoices.append(choice)
        xChoices.append(-(choice))
    elif letter == "x":
        xChoices.append(choice)
        oChoices.append(-(choice))
    spot = unFlattenBoard(choice)
    return spot

def selectCellSmart(origBoard, rewardBoard, curEpoch, move):
    board = []
    for row in range(3):
        for column in range(3):
            if origBoard[row][column] == 0:
                board = flattenBoard(board,row,column)
    #print(board)
    #Implement Choice based on past rewards and loses
    choice = determineBestCell(board, curEpoch, rewardBoard, move)
    spot = unFlattenBoard(choice)
    return spot

#selectCellSmart(grid, oBoard, currentEpoch, len(oChoices))

def chooseMove(board, letter):
    spot = randomlySelectCell(board, letter)
    if letter == "o":
        board[spot.row][spot.column] = 2;
        turn = 1
    if letter == "x":
        board[spot.row][spot.column] = 1;
        turn = 2

def trian():
    trial = 1
    while trial == 1:
        for i in range(0, 1):
            i+=1
            if i == 1:
                trial=2


'''Was exploring Different Methods of learning

class Agent(object):
    def __init__(self, exploration_rate=0.33, learning_rate=0.5, discount-factor=0.01):
        self.states = {}
        self.state_order = []
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

    def getSerious(self):
        self.exploration_rate = 0

    def learn_by_temporal_difference(self, reward, new_state_key, state_key):
        old_state = self.states.get(state_key, np.zeros((3,3)))
        return self.learning_rate * ((reward * self.states[new_state_key]) - old_state)

class Bot1(object):
    def__init__(self)
        self.Trial = 1
        self.Moves[Epoch] =
'''

def events(game):
    global mode, turn, grid, crashed, realTime, displayGame
    ev = game.event.get()
    pos = game.mouse.get_pos()
    pressed1, pressed2, pressed3 = game.mouse.get_pressed()
    for event in ev:
        if event.type == game.KEYDOWN:
            if event.key == K_r:
                realTime = True
                mode = Mode.PVB
                print("Reset options!")
            if event.key == K_1:
                mode = Mode.PVP
                print("Mode changed to " + str(mode))
            if event.key == K_2:
                mode = Mode.PVB
                print("Mode changed to " + str(mode))
            if event.key == K_3:
                mode = Mode.BVB
                print("Mode changed to " + str(mode))
            if event.key == K_4:
                realTime^=True
                print("Real time switched!")
            if event.key == K_ESCAPE:
                crashed = True
            if event.key == K_5:
                smartResult^=True
            if event.key == K_6:
                displayGame^=True
        if event.type == game.MOUSEBUTTONDOWN:
            column = pos[0] // (width+margin)
            row = pos[1] // (height+margin)
            #print("Click ", pos, "Grid coordinates: ", row, column)
            if grid[row][column] == 0 and not mode == Mode.BVB:
                if turn==1:
                    grid[row][column] = 1
                    turn = 2
                elif turn==2 and mode == Mode.PVP:
                    grid[row][column] = 2
                    turn=1
        if event.type == game.QUIT:
            crashed = True

while not crashed:
    events(pygame)
    if currentEpoch == epochs+1 and sTurn==1:
        currentEpoch=1
        sTurn=2
        turn=2
        print("sTurn is now 2, next set of generations started!")
    if currentEpoch == epochs+1 and sTurn==2:
        saveFiles()
        crashed = True
    if displayGame:
        gameDisplay.fill(black)
        for row in range(3):
            for column in range(3):
                if grid[row][column] == 0:
                    pygame.draw.rect(gameDisplay, white, [(bar + width) * column + margin, (bar + height) * row + margin, width, height])
                if grid[row][column] == 1:
                    gameDisplay.blit(xImg, ((bar + width) * column + margin, (bar + height) * row + margin))
                if grid[row][column] == 2:
                    gameDisplay.blit(oImg, ((bar + width) * column + margin, (bar + height) * row + margin))

        xSurface = font.render('X Wins: ' + str(xWins), False, green)
        oSurface = font.render('O Wins: ' + str(oWins), False, green)
        drawsSurface = font.render('Draws: ' + str(draws), False, green)
        draws_rect = drawsSurface.get_rect(center=(tWidth/2, tHeight-30))
        gameDisplay.blit(xSurface, (25,0))
        gameDisplay.blit(oSurface, (tWidth-(len(str('O Wins: ' + str(oWins)))*10)-75,0))
        gameDisplay.blit(drawsSurface, draws_rect)
        pygame.display.update()

    if(isWinner(grid, 1)):
        xWins+=1
        turn = sTurn
        #sTurn = 1
        if realTime:
            pygame.time.delay(1000)
        resetBoard("x")

    elif(isWinner(grid, 2)):
        oWins+=1
        turn = sTurn
        #sTurn = 1
        if realTime:
            pygame.time.delay(1000)
        resetBoard("o")

    elif(isDraw(grid)):
        draws+=1
        turn = sTurn
        #sTurn = 1
        if realTime:
            pygame.time.delay(1000)
        resetBoard("draw")

    if turn == 2 and (mode == Mode.PVB or mode == Mode.BVB):
        if realTime:
            pygame.time.delay(1000)
        chooseMove(grid, "o")
        #selectCellSmart(grid, oBoard, currentEpoch, len(oChoices))
        turn = 1
    elif turn == 1 and mode == Mode.BVB:
        if realTime:
            pygame.time.delay(1000)
        chooseMove(grid, "x")
        #selectCellSmart(grid, oBoard, currentEpoch, len(oChoices))
        turn = 2

    clock.tick(60)

#if crashed:

pygame.quit()
quit()
