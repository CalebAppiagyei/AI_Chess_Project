'''

Name: Caleb Appiagyei

Date: 1/10/23

Description: Creating a playable chess ai
'''

import random

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
pieceScore = {"K" : 0, "Q" : 8, "R" : 5, "B" : 3, "N" : 3, "p" : 1}
CHECKMATE = 1000
STALEMATE = 0

# Returning a random move from the list of valid moves
def findRandomMove(validMoves):
   return validMoves[random.randint(0, len(validMoves) - 1)] # Inclusive of both elements

# Finding the best move using the 'greedy' algorithm
def findBestMove(gameState, validMoves):
    turnMultiplier = 1 if gameState.whiteToMove else -1 
    maxScore = -CHECKMATE # -1000 is the worst possible score for white
    bestMove = None
    score = maxScore
    
    for playerMove in validMoves:
        gameState.makeMove(playerMove)
        if gameState.checkMate: 
            score = CHECKMATE
        elif gameState.staleMate:
            score = STALEMATE
        else:
            score = scorePieces(gameState.board) * turnMultiplier # Making it so that both sides will be attempting to reach the highest score regardless of color
            if score > maxScore:
                maxScore = score
                bestMove = playerMove
        gameState.undoMove()
    return bestMove
        
    

# Scoring the board based on the pieces on the board (does not factor position)
def scorePieces(board): # or scoreMaterial
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]] # If the piece is white add to the score
            elif square[0] == 'b':
                score -= pieceScore[square[1]] # If the piece is black subtract from the score
    return score
    

    

