'''
Name: Caleb Appiagyei

Date: 12/26/22

Description: Stores all of the information about the current state of the
chess game. Also responsible for determining the valid moves at the current
state

Inspiration: Eddie Sharick (Youtube)
'''

# importing the numpy class so that you may use a numpy array
import numpy as np

# Storing each row as its own list so that it is easier to access later on
blankRow = ["--", "--", "--", "--", "--", "--", "--", "--"]
blackRow = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]
blackPawns = ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"]
whiteRow = ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
whitePawns = ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"]
board = [blackRow, blackPawns, blankRow, blankRow, blankRow, blankRow, whitePawns, whiteRow]

class GameState():
    def __init__(self):
        # 8x8 2D list, each element has 2 characters
        # First element represents the color of the piece the second represents the type
        # Two dashes represents an empty space
        # Used a numpy array for efficiency
        self.board = np.array(board)
        self.whiteToMove = True
        self.moveLog = []
        # Saving the initial starting positions of the kings
        self.wKingLoc = (7, 4)
        self.bKingLoc = (0, 4)
        # This will be a dictionary that maps every letter (representing a piece) to its necessary function
        self.moveFunctions = {
            'p' : self.getPawnMoves,
            'R' : self.getRookMoves,
            'N' : self.getKnightMoves,
            'B' : self.getBishopMoves,
            'Q' : self.getQueenMoves,
            'K' : self.getKingMoves
        }
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.currentCastlingRight = CastleRights(True, True, True, True) # In the beginning the castling rights are all true
        self.castleRightLog = [
                CastleRights(self.currentCastlingRight.whiteKingSide,
                self.currentCastlingRight.whiteQueenSide,
                self.currentCastlingRight.blackKingSide,
                self.currentCastlingRight.blackQueenSide,
            )] # Keeping a log of the castling rights

    # Making the move
    # Takes a move as the parameter and executes it
    # Works for every move except castling pawn promotion and the "en passant" rule
    def makeMove(self, move):
        self.board[move.startRow][move.startColo] = "--"
        self.board[move.endRow][move.endColo] = move.pieceMoved
        self.moveLog.append(move) # Adds the move to the move log in case we want to undo the move or review the history of the game
        self.whiteToMove = not self.whiteToMove
        # Update the locations of the kings
        if move.pieceMoved == 'wK':
            self.wKingLoc = (move.endRow, move.endColo)
        elif move.pieceMoved == 'bK':
            self.bKingLoc = (move.endRow, move.endColo)
        # Pawn Promotion (Automatically makes it a queen)
        if move.isPawnPromo:
            self.board[move.endRow][move.endColo] = move.pieceMoved[0] + 'Q'
        # En Passant
        if move.isEnPassant:
            self.board[move.startRow][move.endColo] = '--' # Capturing the pawn
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # En passant can only happen after a 2 square advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startColo)
        else: 
            self.enpassantPossible = ()

        # Making the castle move
        if move.isCastleMove:
            if move.endColo - move.startColo == 2: # Determining if it was a king or queen side castle move
                self.board[move.endRow][move.endColo - 1] = self.board[move.endRow][move.endColo + 1] # Copies the rook to its new square
                self.board[move.endRow][move.endColo + 1] = '--' # Removing the old rook
            else: # Queen side castle move
                self.board[move.endRow][move.endColo + 1] = self.board[move.endRow][move.endColo - 2] # Copies the rook (King moves more further when it is a queen side move)
                self.board[move.endRow][move.endColo - 2] = '--' # Removing the old rook

        # Updating the Castling rights (whenever there is a rook or king move)
        self.updateCastleRights(move)
        self.castleRightLog.append(
                CastleRights(self.currentCastlingRight.whiteKingSide,
                self.currentCastlingRight.blackKingSide,
                self.currentCastlingRight.whiteQueenSide,
                self.currentCastlingRight.blackQueenSide,
            ))



    # Undoes the last move
    def undoMove(self):
        if len(self.moveLog) != 0: # Makes sure that there is a move to be undone
            oldMove = self.moveLog.pop() # The pop function returns the final element in the tuple and removes it
            self.board[oldMove.startRow][oldMove.startColo] = oldMove.pieceMoved
            self.board[oldMove.endRow][oldMove.endColo] = oldMove.pieceCaptured # If the piece captured is just an empty space it will go back to an empty space
            # Update the locations of the kings
            if oldMove.pieceMoved == 'wK':
                self.wKingLoc = (oldMove.startRow, oldMove.startColo)
            elif oldMove.pieceMoved == 'bK':
                self.bKingLoc = (oldMove.startRow, oldMove.startColo)
            self.whiteToMove = not self.whiteToMove # Switch turns
            # Undoing an en passant move
            if oldMove.isEnPassant:
                self.board[oldMove.endRow][oldMove.endColo] = '--' # Making the landing square blank
                self.board[oldMove.startRow][oldMove.endColo] = oldMove.pieceCaptured
                self.enpassantPossible = (oldMove.endRow, oldMove.endColo)
            if oldMove.pieceMoved[1] == 'p' and abs(oldMove.startRow - oldMove.endRow) == 2:
                self.enpassantPossible = ()
            # Undoing the castling rights
            self.castleRightLog.pop()
            oldRights = self.castleRightLog[-1] # Set the current castle rights to the last one in the list
            self.currentCastlingRight = CastleRights(oldRights.whiteKingSide, oldRights.blackKingSide, oldRights.whiteQueenSide, oldRights.blackQueenSide)
            # Undoing the castle move
            if oldMove.isCastleMove:
                if oldMove.endColo - oldMove.startColo == 2: # King side
                    self.board[oldMove.endRow][oldMove.endColo + 1] = self.board[oldMove.endRow][oldMove.endColo - 1]
                    self.board[oldMove.endRow][oldMove.endColo - 1] = '--'
                else: # Queen side
                    self.board[oldMove.endRow][oldMove.endColo - 2] = self.board[oldMove.endRow][oldMove.endColo + 1]
                    self.board[oldMove.endRow][oldMove.endColo + 1] = '--'



    # Updating the castle rights based on the move made on the board
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.whiteKingSide = False
            self.currentCastlingRight.whiteQueenSide = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.blackKingSide = False
            self.currentCastlingRight.blackQueenSide = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startColo == 0: # Left Rook
                    self.currentCastlingRight.whiteQueenSide = False
                elif move.startColo == 7: # Right Rook
                    self.currentCastlingRight.whiteKingSide = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startColo == 0: # Left Rook
                    self.currentCastlingRight.blackQueenSide = False
                elif move.startColo == 7: # Right Rook
                    self.currentCastlingRight.blackKingSide = False


    # All valid moves (checks included)
    def getValidMoves(self):
        # Copying the current enPassant and castling rights
        tempEnPassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.whiteKingSide, self.currentCastlingRight.blackKingSide,
        self.currentCastlingRight.whiteQueenSide, self.currentCastlingRight.blackQueenSide)
        moves = self.getAllMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.wKingLoc[0], self.wKingLoc[1], moves)
        else:
            self.getCastleMoves(self.bKingLoc[0], self.bKingLoc[1], moves)
        for i in range(len(moves)-1, -1, -1): # When removing from a list it is best to start from the back that way you will not have issues with the index
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) # If the move attacks your king, it is not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # In this case it would either be a checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else: # Undoing it after testing certain moves
            self.checkMate = False
            self.staleMate = False
        self.enpassantPossible = tempEnPassantPossible # Making sure the value does not change after the engine generates the valid moves
        self.currentCastlingRight = tempCastleRights # Resetting the castle rights
        return moves

    # Checks for when a player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.underAttack(self.wKingLoc[0], self.wKingLoc[1])
        else:
            return self.underAttack(self.bKingLoc[0], self.bKingLoc[1])

    # Checks if the enemy can attack the square at the given coordinate (r, c)
    def underAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # Switching to the opponents point of view
        oppMoves = self.getAllMoves()
        self.whiteToMove = not self.whiteToMove # Switching turns back
        for oppMove in oppMoves:
            if oppMove.endRow == r and oppMove.endColo == c: # The given square is in danger
                return True
        return False

    # All possible moves (checks not included) *getAllMoves == getAllPossibleMoves*
    def getAllMoves(self):
        moves = []
        for row in range(len(self.board)): # Rows
            for colo in range(len(self.board[row])): # Coloumns for each row
                coord = self.board[row][colo]
                turn = coord[0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove): # If the piece is white and it is their turn or if the piece is black and it is not the white's turn
                    piece = coord[1]
                    self.moveFunctions[piece](row, colo, moves) # Calls the appropriate move function so that you do not need multiple if statements
        return moves

    
    # Generates all of the possible pawn moves of the given pawn and adds it to a list
    def getPawnMoves(self, row, colo, moves):
        # White Pawn moves
        if self.whiteToMove: # If it is white's turn
            if self.board[row - 1][colo] == "--": # If the block ahead is empty
                moves.append(Move((row, colo),(row - 1, colo), self.board)) # Adds a one square move if the block ahead is empty
                if row == 6 and self.board[row - 2][colo] == "--": # If the there are 2 blank squares ahead and it is the first pawn move (meaning it is in row 6)
                    moves.append(Move((row, colo), (row - 2, colo), self.board))
            # Pawn Captures
            if colo - 1 >= 0: # Making sure the piece does not go off the board
                # Captures to the left
                if self.board[row - 1][colo - 1][0] == 'b': # If the piece that is in the the diagonal position is black
                    moves.append(Move((row, colo), (row - 1, colo - 1), self.board)) 
                elif (row - 1, colo - 1) == self.enpassantPossible:
                    moves.append(Move((row, colo), (row - 1, colo - 1), self.board, enpassantMove=True)) 
            if colo + 1 <= 7: # Making sure the piece does not go off the board
                # Captures to the right
                if self.board[row - 1][colo + 1][0] == 'b': # If the piece is black
                    moves.append(Move((row, colo), (row - 1, colo + 1), self.board))
                elif (row - 1, colo + 1) == self.enpassantPossible:
                    moves.append(Move((row, colo), (row - 1, colo + 1), self.board, enpassantMove=True)) 
        # Black Pawn moves
        else: # If it is not white's turn it is black's turn
            if self.board[row + 1][colo] == "--": # If the block ahead is empty
                moves.append(Move((row, colo), (row + 1, colo), self.board)) # Adds a one block move to the possible moves
                if row == 1 and self.board[row + 2][colo] == "--": # If there are two empty spots ahead
                    moves.append(Move((row, colo), (row + 2, colo), self.board))
            # Pawn captures
            if colo - 1 >= 0: # Making sure the piece does not go off the board
                # Captures to the left (black's right)
                if self.board[row + 1][colo - 1][0] == 'w': # If the diagonal piece is white
                    moves.append(Move((row, colo), (row + 1, colo - 1), self.board)) # Adding the new move
                elif (row + 1, colo - 1) == self.enpassantPossible:
                    moves.append(Move((row, colo), (row + 1, colo - 1), self.board, enpassantMove=True)) 
            if colo + 1 <= 7: # Making sure the piece does not go off the board
                # Captures to the right (black's left)
                if self.board[row + 1][colo + 1][0] == 'w': # If the diagonal piece is white
                    moves.append(Move((row, colo), (row + 1, colo + 1), self.board)) # Adding the new move
                elif (row + 1, colo + 1) == self.enpassantPossible:
                    moves.append(Move((row, colo), (row + 1, colo + 1), self.board, enpassantMove=True)) 

    '''
    Generates all of the possible rook moves of the given rook and adds it to a list
    '''
    def getRookMoves(self, row, colo, moves): # *May possibly revise to a shorter solution similar to bishop moves*
        # White Rook moves
        if self.whiteToMove: # If it is white's turn
            # Start adding possible forward moves
            forwardCount = row - 1 # Start from the first square ahead
            while forwardCount >= 0: # Making sure it does not go off the board
                if self.board[forwardCount][colo][0] == 'b': # If the piece in that coordinate is black
                    moves.append(Move((row, colo), (forwardCount, colo), self.board))
                    break # The rook can not go past the black piece
                elif self.board[forwardCount][colo][0] == 'w': # If the piece in that coordinate is white
                    break
                else:
                    moves.append(Move((row, colo), (forwardCount, colo), self.board))
                forwardCount = forwardCount - 1
            # Start adding possible backward moves
            backwardCount = row + 1 # Start from the first square behind
            while backwardCount <= 7: # Making sure it does not go off the board
                if self.board[backwardCount][colo][0] == 'b': # If the piece is black
                    moves.append(Move((row, colo), (backwardCount, colo), self.board))
                    break
                elif self.board[backwardCount][colo][0] == 'w': # If the piece in that coordinate is white
                    break
                else: 
                    moves.append(Move((row, colo), (backwardCount, colo), self.board))
                backwardCount = backwardCount + 1
            # Start adding possible moves to the left
            leftCount = colo - 1
            while leftCount >= 0: # Making sure the piece does not go off the board
                if self.board[row][leftCount][0] == 'b': # If the piece is black
                    moves.append(Move((row, colo), (row, leftCount), self.board))
                    break
                elif self.board[row][leftCount][0] == 'w': # If the piece is white
                    break
                else:
                    moves.append((Move((row, colo), (row, leftCount), self.board)))
                leftCount = leftCount - 1
            # Start adding possible moves to the right
            rightCount = colo + 1
            while rightCount <= 7: # Making sure the piece does not go off the board
                if self.board[row][rightCount][0] == 'b': # If the piece is black
                    moves.append(Move((row, colo), (row, rightCount), self.board))
                    break
                elif self.board[row][rightCount][0] == 'w': # If the piece is white
                    break
                else:
                    moves.append(Move((row, colo), (row, rightCount), self.board))
                rightCount = rightCount + 1
        else: # If it is not white's turn it is black's turn
            # Start adding possible forward moves
            forwardCount = row + 1 # Start from the first square ahead
            while forwardCount <= 7: # Making sure it does not go off the board
                if self.board[forwardCount][colo][0] == 'w': # If the piece in that coordinate is white
                    moves.append(Move((row, colo), (forwardCount, colo), self.board))
                    break # The rook can not go past the white piece
                elif self.board[forwardCount][colo][0] == 'b': # If the piece in that coordinate is black
                    break
                else:
                    moves.append(Move((row, colo), (forwardCount, colo), self.board))
                forwardCount = forwardCount + 1
            # Start adding possible backward moves
            backwardCount = row - 1 # Start from the first square behind
            while backwardCount >= 0: # Making sure it does not go off the board
                if self.board[backwardCount][colo][0] == 'w': # If the piece is white
                    moves.append(Move((row, colo), (backwardCount, colo), self.board))
                    break
                elif self.board[backwardCount][colo][0] == 'b': # If the piece in that coordinate is black
                    break
                else: 
                    moves.append(Move((row, colo), (backwardCount, colo), self.board))
                backwardCount = backwardCount - 1
            # Start adding possible moves to black's left
            leftCount = colo + 1
            while leftCount <= 7: # Making sure the piece does not go off the board
                if self.board[row][leftCount][0] == 'w': # If the piece is white
                    moves.append(Move((row, colo), (row, leftCount), self.board))
                    break
                elif self.board[row][leftCount][0] == 'b': # If the piece is black
                    break
                else:
                    moves.append((Move((row, colo), (row, leftCount), self.board)))
                leftCount = leftCount + 1
            # Start adding possible moves to black's right
            rightCount = colo - 1
            while rightCount >= 0: # Making sure the piece does not go off the board
                if self.board[row][rightCount][0] == 'w': # If the piece is white
                    moves.append(Move((row, colo), (row, rightCount), self.board))
                    break
                elif self.board[row][rightCount][0] == 'b': # If the piece is black
                    break
                else:
                    moves.append(Move((row, colo), (row, rightCount), self.board))
                rightCount = rightCount - 1
    '''            
    Generates all of the possible Knight moves of the given Knight and adds it to a list
    '''
    def getKnightMoves(self, row, colo, moves):
        spots = [
            (row - 2, colo + 1),
            (row - 1, colo + 2),
            (row + 1, colo + 2),
            (row + 2, colo + 1),
            (row - 2, colo - 1),
            (row - 1, colo - 2),
            (row + 1, colo - 2),
            (row + 2, colo - 1),
        ]
        if self.whiteToMove: # If it is white's turn
            for spot in spots:
                if 0 <= spot[0] < 8 and 0 <= spot[1] < 8: # If the coordinate is on the board
                    if self.board[spot][0] != 'w': # If there is not a white piece at that coordinate
                        moves.append(Move((row, colo), spot, self.board))
        else: # If it is not white's turn it is black's turn
            for spot in spots:
                if 0 <= spot[0] < 8 and 0 <= spot[1] < 8: # If the coordinate is on the board
                    if self.board[spot][0] != 'b': # If there is not a black piece at that coordinate
                        moves.append(Move((row, colo), spot, self.board))

    '''
    Generates all of the possible Bishop moves of the given Bishop and adds it to a list
    '''
    def getBishopMoves(self, row, colo, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # 4 diagonals
        enemy = 'b' if self.whiteToMove else 'w'
        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endColo = colo + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endColo < 8: # Staying on the board
                    endPiece = self.board[endRow][endColo]
                    if endPiece == "--": # Theres an empty space
                        moves.append(Move((row, colo), (endRow, endColo), self.board))
                    elif endPiece[0] == enemy: # Opposite color
                        moves.append(Move((row, colo), (endRow, endColo), self.board))
                        break
                    else: # Cant skip over an ally piece
                        break
                else: # That spot is off the board
                    break


            

    '''
    Generates all of the possible Queen moves of the given Queen and adds it to a list
    '''    
    def getQueenMoves(self, row, colo, moves):
        self.getRookMoves(row, colo, moves)
        self.getBishopMoves(row, colo, moves)

    '''
    Generates all of the possible King moves of the given King and adds it to a list
    '''
    def getKingMoves(self, row, colo, moves):
        spots = [ 
            (row - 1, colo - 1),
            (row - 1, colo),
            (row - 1, colo + 1),
            (row, colo - 1),
            (row, colo + 1),
            (row + 1, colo - 1),
            (row + 1, colo),
            (row + 1, colo + 1),
        ]
        allyColor = 'w'
        if self.whiteToMove: # If it is white's turn
            for spot in spots:
                if 0 <= spot[0] < 8 and 0 <= spot[1] < 8: # If the coordinate is on the board
                    if self.board[spot][0] != 'w': # If there is not a white piece at that coordinate
                        moves.append(Move((row, colo), spot, self.board))
        else: # If it is not white's turn it is black's turn
            allyColor = 'b'
            for spot in spots:
                if 0 <= spot[0] < 8 and 0 <= spot[1] < 8: # If the coordinate is on the board
                    if self.board[spot][0] != 'b': # If there is not a black piece at that coordinate
                        moves.append(Move((row, colo), spot, self.board))
        

    # Generates all valid castle moves for the king
    def getCastleMoves(self, row, colo, moves):
        if self.underAttack(row, colo):
            return # You cannot castle if you are in check
        if (self.whiteToMove and self.currentCastlingRight.whiteKingSide) or (not self.whiteToMove and self.currentCastlingRight.blackKingSide):
            self.getKingSideCastleMoves(row, colo, moves)
        if (self.whiteToMove and self.currentCastlingRight.whiteQueenSide) or (not self.whiteToMove and self.currentCastlingRight.blackQueenSide):
            self.getQueenSideCastleMoves(row, colo, moves)            

    # Handles possible castle moves to the king's side
    def getKingSideCastleMoves(self, row, colo, moves):
        if self.board[row][colo + 1] == '--' and self.board[row][colo + 2] == '--':
            if not self.underAttack(row, colo + 1) and not self.underAttack(row, colo + 2):
                moves.append(Move((row, colo), (row, colo + 2), self.board, isCastleMove = True))


    # Handles possible castle moves to the queen's side
    def getQueenSideCastleMoves(self, row, colo, moves):
        if self.board[row][colo - 1] == '--' and self.board[row][colo - 2] == '--' and self.board[row][colo - 3] == '--':
            if not self.underAttack(row, colo - 1) and not self.underAttack(row, colo - 2):
                moves.append(Move((row, colo), (row, colo - 2), self.board, isCastleMove = True))

# Stores the current state of the castling possibilities
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.whiteKingSide = wks
        self.blackKingSide = bks
        self.whiteQueenSide = wqs
        self.blackQueenSide = bqs

class Move():
    # maps keys to values
    # key : value
    # In chess each square has its own rank-file notation for example the top left of a chess board from whites perspective is a8
    # however, in python it is point (0,0)
    # The following is a dictionary that equates the algebraic notation to the python coordinate
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4, "5" : 3, "6" : 2, "7" : 1, "8" : 0} # Converts the "rank" on a chess board to the corresponding python coordinate value
    rowsToRanks = {v: k for k, v in ranksToRows.items()} # makes a dictionary that swaps the keys and values in ranksToRows
    filesToCols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7} # Converts the "file" on a chess board to the corresponding python coordinate value
    colsToFiles = {v : k for k, v in filesToCols.items()} # makes a dictionary that swaps the keys and values in filesToCols
    def __init__(self, startSquare, endSquare, board, enpassantMove=False, isCastleMove = False): # enpassantPossible is an optional parameter 
        self.startRow = startSquare[0]
        self.startColo = startSquare[1]
        self.endRow = endSquare[0]
        self.endColo = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startColo]
        self.pieceCaptured = board[self.endRow][self.endColo]
        self.moveID = (self.startRow * 1000) + (self.startColo * 100) + (self.endRow * 10) + self.endColo # Making a number that contains the starting and ending coordinates of the move
        # Handling pawn promotion
        self.isPawnPromo = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # Handling en passant
        self.isEnPassant = enpassantMove
        if self.isEnPassant:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # Castle Move
        self.isCastleMove = isCastleMove

    # Overriding the equals method (we have to use this because we made a move clas)
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    # Gets the rank-file notation of the start point and endpoint of the move
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startColo) + " to " + self.getRankFile(self.endRow, self.endColo)

    # Gets the rank-file notation of the given coordinate on the board
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


    
        