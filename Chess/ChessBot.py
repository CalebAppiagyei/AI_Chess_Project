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


    

    

