'''

Name: Caleb Appiagyei

Date: 1/10/23

Description: Creating a playable chess ai
'''

import random
import numpy as np

'''
Dictionary of scores for each piece
King was not given a score because if the King is gone then the game is already over
Queen was given an eight becuase it can do the job of a rook and a bishop who each 
have scores of 5 and 3
The closer the ai gets to 1000 for a checkmate, the better
A stalemate is zero because it is better than losing (which would be negative), but
the ai is not winning (which would be positive)
White is trying to get to 1000 and black is trying to get to -1000
'''
pieceScore = {"K" : 0.0, "Q" : 8.0, "R" : 5.0, "B" : 3.0, "N" : 3.0, "p" : 1.0}
CHECKMATE = 1000.0
STALEMATE = 0.0
DEPTH = 2

# Returning a random move from the list of valid moves
def findRandomMove(validMoves):
   return validMoves[random.randint(0, len(validMoves) - 1)] # Inclusive of both elements

'''
Finding the best move using a "MinMax" algorithm
This algorithm is similar to the greedy algorithm however
it looks at the possible moves the opponent can make and evaluates 
the scores for the opponent so it can attempt to maximize its own
score while minimizing the opponents score. (In other words it is 
now not only trying to get the best score for itself, but it is also
trying to put the opponent in a worse position so they can not increase
their score as much)
'''
def findBestMove(gameState, validMoves): # Could possibly alter the contents
    turnMultiplier = 1 if gameState.whiteToMove else -1 
    opponentMinMaxScore = CHECKMATE # -1000 is the worst possible score for white
    bestMove = None
    random.shuffle(validMoves) # Shuffling the list of moves so that the ai does not choose the same move when multiple moves have the same score
    for playerMove in validMoves:
        gameState.makeMove(playerMove)
        opponentsMoves = gameState.getValidMoves()
        if gameState.staleMate:
            opponentsMaxScore = STALEMATE
        elif gameState.checkMate:
            opponentsMaxScore = -CHECKMATE
        else:
            opponentsMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gameState.makeMove(opponentsMove)
                gameState.getValidMoves() # This line reduces some efficiency
                if gameState.checkMate: 
                    score = CHECKMATE
                elif gameState.staleMate:
                    score = STALEMATE
                else:
                    score = scorePieces(gameState.board) * -turnMultiplier # Making it so that both sides will be attempting to reach the highest score regardless of color
                    if score > opponentsMaxScore:
                        opponentsMaxScore = score
                gameState.undoMove()
        # Minimizing the opponents move
        if opponentsMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentsMaxScore
            bestMove = playerMove
        gameState.undoMove()
    return bestMove


'''
The find move minmax functions are minmax algorithms with recursion
with this method I am able to do the same thing as the find best move
function however I can have more depth (look further ahead into the game)
The above findbestmove function also looks ahead however, in order to 
increase the depth I would have to legnthen the code. With the recursive
MinMax method, I can simpky choose how far I want to look ahead by changing
the DEPTH variable at the top and it will look that far ahead
'''
# Helper function for findMoveMinMax
def findBestMoveMinMax(gameState, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gameState, validMoves, DEPTH, gameState.whiteToMove)
    return nextMove

def findMoveMinMax(gameState, validMoves, depth, whiteToMove): # depth represents how many moves you want to look ahead to
    global nextMove
    if depth == 0: # Terminal node
        return scorePieces(gameState.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return minScore
            

      
pawnValues = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
    [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
    [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
    [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
    [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
]
pawnValues = np.array(pawnValues)

knightValues = [
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
    [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
    [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
    [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
    [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
]
knightValues = np.array(knightValues)

bishopValues = [
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
    [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
    [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
    [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
    [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
]
bishopValues = np.array(bishopValues)

rookValues = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
]
rookValues = np.array(rookValues)

queenValues = [
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
]
queenValues = np.array(queenValues)

zeros = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
kingValues = [zeros, zeros, zeros, zeros, zeros, zeros, zeros, zeros]
kingValues = np.array(kingValues)

values = {
    'K' : kingValues,
    'Q' : queenValues,
    'B' : bishopValues,
    'R' : rookValues,
    'N' : knightValues,
    'p' : pawnValues
}

# Scoring the board based on the pieces on the board (does not factor position)
def scorePieces(board): # or scoreMaterial
    score = 0.0
    # Giving every piece on the board a score
    for row in range(7):
        for colo in range(7):
            square = board[row][colo]
            if square[0] == 'w':
                score += pieceScore[square[1]] # If the piece is white add to the score
                score = score + float(values[square[1]][row][colo])
            elif square[0] == 'b':
                score -= pieceScore[square[1]] # If the piece is black subtract from the score
                score = score - float(values[square[1]][row][colo])
    return score


# A positive score from this function is good for white and a negative score from this is good for black
def scoreBoard(gameState):
    board = gameState.board
    if gameState.checkMate:
        if gameState.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gameState.staleMate:
        return STALEMATE
    score = 0.0
    # Giving every piece on the board a score
    for row in range(7):
        for colo in range(7):
            square = board[row][colo]
            if square[0] == 'w':
                score += pieceScore[square[1]] # If the piece is white add to the score
                score = score + float(values[square[1]][row][colo])
            elif square[0] == 'b':
                score -= pieceScore[square[1]] # If the piece is black subtract from the score
                score = score - float(values[square[1]][row][colo])
    return score
    

    

