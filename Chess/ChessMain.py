'''
Name: Caleb Appiagyei

Date: 12/26/22

Description: Chess driver file. Responsible for handling user input
and displaying the current GameState object

Inspiration: Eddie Sharick (Youtube)
'''

import pygame as p
from ChessEngine import GameState
from ChessEngine import Move

WIDTH = HEIGHT = 512 #400 is another good option
DIMENSION = 8 #Chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION # Double division sign gives your answer in integers
MAX_FPS = 15 # For animations 
IMAGES ={}

'''
Will initialize a global dictionary of images. This will be called exactly once in the main
'''

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # We can access an image by calling 'IMAGES['type of piece']

'''
Main driver for the code.
This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock() 
    screen.fill(p.Color("white")) # Background color
    gameState = GameState() 
    validMoves = gameState.getValidMoves() # This statement decreases our efficiency which is why we have the statement following
    moveMade = False # Flag variable for when the move is made
    animate = False # Boolean that determines whether or not a move should be animated
    gameOver = False
    loadImages() # This is only done once
    running = True
    squareSelected = () # Keeps track of the last click from the user in a tuple (row, coloumn)
    playerClicks = [] # Keep track of player clicks (two tuples[(6,4), (4,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse 
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # (x, y) location of mouse
                    colo = location[0] // SQ_SIZE 
                    row = location[1] // SQ_SIZE
                    if squareSelected == (row, colo): # Checks to make sure that the square that the user selects isnt the same as what was selected before it
                        squareSelected = () # Deselects that square if that is the case
                        playerClicks = [] # Clears the player clicks
                    else:
                        squareSelected = (row, colo)
                        playerClicks.append(squareSelected) # adds the locations of the first and second clicks to the tuple
                    if len(playerClicks) == 2: # Once the player has made two clicks in different squares (meaning that they are attempting to make a move with a piece)
                        move = Move(playerClicks[0], playerClicks[1], gameState.board) # Making the move
                        for i in range(len(validMoves)):
                            if move == validMoves[i]: # Only make the move if the move is a valid move
                                gameState.makeMove(validMoves[i])
                                print(move.getChessNotation())
                                moveMade = True
                                animate = True
                                squareSelected = () # Reset the user clicks so that they can continue making moves
                                playerClicks = [] # Clears the player clicks
                        if not moveMade: # Helps if a user misclicks or changes their mind on what piece to move
                            playerClicks = [squareSelected] 
            # If the user presses a key
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u: # Undo the move when 'u' is pressed
                    gameState.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: # Reset the board when the user presses 'r'
                    gameState = GameState()
                    validMoves = gameState.getValidMoves
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    
        if moveMade:
            if animate:
                animateMove(gameState.moveLog[-1], screen, gameState.board, clock)
            validMoves = gameState.getValidMoves()
            moveMade = False
            animate = False
            

        drawGameState(screen, gameState, validMoves, squareSelected)
        if gameState.checkMate:
            gameOver = True
            if gameState.whiteToMove:
                drawText(screen, 'Black wins by checkmate', gameState)
            else:
                drawText(screen, 'White wins by checkmate', gameState)
        elif gameState.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate', gameState)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlighting the piece and the possible moves it can make
'''
def HighlightSquares(screen, gameState, validMoves, sqSelected, moveLog):
    if sqSelected != (): # Making sure that the square selected is not empty
        r, c = sqSelected # Coordinates of the selected square
        if gameState.board[r][c][0] == ('w' if gameState.whiteToMove else 'b'): # Making sure the piece selected can be moved
            # Highlight the selected square using the transparency feature
            s = p.Surface((SQ_SIZE, SQ_SIZE)) # Using the coordinate as one parameter
            s.set_alpha(100) # Transparency value (0 is completely transparent and 255 is solid color)
            s.fill(p.Color("brown")) # Make the selected square the color given
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # Highlight the moves that piece can make
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startColo == c:
                    screen.blit(s, (SQ_SIZE * move.endColo, SQ_SIZE * move.endRow))
            # Highlight the last move that was made
            if len(moveLog) > 0:
                s.set_alpha(125)
                s.fill(p.Color("red"))
                screen.blit(s, (SQ_SIZE * moveLog[-1].endColo, SQ_SIZE * moveLog[-1].endRow))
                screen.blit(s, (SQ_SIZE * moveLog[-1].startColo, SQ_SIZE * moveLog[-1].startRow))

'''
Displays the graphics of the current game state
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # Draws the squares on the board
    #HighlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draws the pieces on top of the squares
    HighlightSquares(screen, gs, validMoves, sqSelected, gs.moveLog)

'''
Draws the squares on the board
'''
def drawBoard(screen):
    global colors # creating a global colors field
    colors = [p.Color("cornsilk"), p.Color("olivedrab")] # Choosing the colors for the board
    for row in range(DIMENSION):
        for colo in range(DIMENSION):
            color = colors[((row + colo) % 2)] # Assigns the color of the square based on the remainder of the sum of the row and coloumn values even is light odd is dark
            p.draw.rect(screen, color, p.Rect(colo * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)) # Drawing them row by coloumn

'''
Draws the pieces on the board based on the current gamestate
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for colo in range(DIMENSION):
            piece = board[row][colo]
            if piece != "--": # If the piece is not an empty square then draw the piece
                screen.blit(IMAGES[piece], p.Rect(colo * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating the moves
'''
def animateMove(move, screen, board, clock):
    global colors
    deltaRow = move.endRow - move.startRow
    deltaColo = move.endColo - move.startColo
    framesPerSquare = 10 # frames to move one square
    frameCount = (abs(deltaRow) + abs(deltaColo)) * framesPerSquare
    for frame in range(frameCount + 1): # Plus 1 includes ending location
        r, c = (move.startRow + deltaRow * frame / frameCount, move.startColo + deltaColo * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endColo) % 2]
        endSquare = p.Rect(move.endColo * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Drawing the captured piece into the rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120) # Frames per second
    
def drawText(screen, text, gameState):
    font = p.font.SysFont("Helvitca", 32, True, False) # Font for end of game message (font name, font size, bold?, italicized?)
    if gameState.checkMate:
        if gameState.whiteToMove:
            textObj = font.render(text, 0, p.Color('Black')) # Font and color
        else:
            textObj = font.render(text, 0, p.Color('burlywood1')) # Font and color
    elif gameState.staleMate:
            textObj = font.render(text, 0, p.Color('chocolate1')) # Font and color
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObj.get_width() / 2, HEIGHT / 2 - textObj.get_height() / 2) # Centering the text
    screen.blit(textObj, textLocation)

# Allows you to use main if it is imported later
if __name__ == "__main__":
    main()


