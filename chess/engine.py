'''
    If you want to play as black or wants to flip the board set :
    self.playerWantsToPlayAsBlack = True
'''

# Responsible for storing all information about current state of chess game, determining valid move, able to undo moves ...


class GameState():
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

        self.board1 = [
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        # set playerWantsToPlayAsBlack = True if you want to flip board and play as black
        self.playerWantsToPlayAsBlack = False
        self.moveLog = []
        # keeping track of king positions to prevent from checks and also it makes castling easier
        if (self.playerWantsToPlayAsBlack):
            self.whiteKinglocation = (0, 4)
            self.blackKinglocation = (7, 4)
        else:
            self.whiteKinglocation = (7, 4)
            self.blackKinglocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.score = 0
        self.pins = []
        self.checks = []
        # co-ordinates for square where enpassant is possible
        self.enpasantPossible = ()
        self.enpasantPossibleLog = [self.enpasantPossible]
        # castling rights
        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        self.castleRightsLog = [castleRights(
            self.whiteCastleKingside, self.whiteCastleQueenside, self.blackCastleKingside, self.blackCastleQueenside)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # save history of the moved played
        self.moveLog.append(move)
        # swap player
        self.whiteToMove = not self.whiteToMove

        # update king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKinglocation = (move.endRow, move.endCol)
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.blackKinglocation = (move.endRow, move.endCol)
            self.blackCastleKingside = False
            self.blackCastleQueenside = False

        # pawn promotion
        # if move.isPawnPromotion:
            # self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # enpassant move
        if move.isEnpassantMove:
            # capture piece, (same row , end col ) is the location of the opponent pawn from our pawn
            self.board[move.startRow][move.endCol] = '--'

        # update enpassant variable everytime piece is moved
        # only on 2 square pawn advances
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            # valid square will be between (startRow and endRow, endcol or startCol(because opponent's pawn 2 square move is on same col))
            # if we do the average of startRow and endRow it will be valid for both black and white
            self.enpasantPossible = (
                (move.startRow + move.endRow)//2, move.startCol)
        else:
            # if after opponent move its pawn to second square instead of capturing it with enpassant we played different move then enpassant move will not be possible
            self.enpasantPossible = ()

        # update Log which side castle is possible
        self.updateCastleRights(move)
        self.castleRightsLog.append(castleRights(
            self.whiteCastleKingside, self.whiteCastleQueenside, self.blackCastleKingside, self.blackCastleQueenside))

        # update enpasantPossibleLog
        self.enpasantPossibleLog.append(self.enpasantPossible)

        # castle moves
        if move.castle:
            # King Side
            if move.endCol - move.startCol == 2:
                # Rook move
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            # Queen Side
            else:
                # Rook move
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

    def undoMove(self):
        if len(self.moveLog) != 0:  # there is atleast one move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # swap player

            # undo updated king's location
            if move.pieceMoved == 'wK':
                self.whiteKinglocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKinglocation = (move.startRow, move.startCol)

            # enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpasantPossibleLog.pop()
            self.enpasantPossible = self.enpasantPossibleLog[-1]

            # give pack castle rights after undo
            self.castleRightsLog.pop()
            castleRights = self.castleRightsLog[-1]
            self.whiteCastleKingside = castleRights.wks
            self.whiteCastleQueenside = castleRights.wqs
            self.blackCastleKingside = castleRights.bks
            self.blackCastleQueenside = castleRights.bqs

            # undo castle
            if move.castle:
                if move.endCol - move.startCol == 2:  # KingSide
                    self.board[move.endRow][move.endCol +
                                            1] = self.board[move.endRow][move.endCol - 1]  # rook move
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queenSide
                    self.board[move.endRow][move.endCol -
                                            2] = self.board[move.endRow][move.endCol + 1]  # rook move
                    self.board[move.endRow][move.endCol + 1] = "--"

            self.checkmate = False
            self.stalemate = False

    # move is valid if your king is in check and you move the piece which stops you from check
    def getValidMoves(self):
        # 1) first generate all possible moves for the piece of player in check
        # 2) for each move, make a move for the player in check
        # 3) generate all opponent moves after you moved-your-piece(when you called makeMove) to prevent check
        # 4) for each of opponents moves, see if opponents still attack your king
        # 5) if they still attack your king, its not a valid move
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKinglocation[0]
            kingCol = self.whiteKinglocation[1]
        else:
            kingRow = self.blackKinglocation[0]
            kingCol = self.blackKinglocation[1]
        if self.inCheck:
            # only one check to the king, move the king or block the check with a piece
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # (row, col) of the piece which is causing the check
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                # position of the piece which is causing the check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # sqaures that pieces can move to
                # if check is from knight than either move the king or take the knight
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        # check[2], check[3] are the check directions
                        validSq = (kingRow + check[2]
                                   * i, kingCol + check[3] * i)
                        validSquares.append(validSq)
                        # upto the piece applying check
                        if validSq[0] == checkRow and validSq[1] == checkCol:
                            break
                # remove the move that dosen't prevent from check
                # going backward in all possible moves
                for i in range(len(moves) - 1, -1, -1):
                    # as the king is not moved it should block the check if not then remove the move from moves
                    if moves[i].pieceMoved[1] != 'K':
                        # if not in validSquares then it do not block check or capture the piece making check
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])  # remove the moves
                    '''
                        till know we will be able to find check and can move piece to block check but we are doing nothing about the pin so it will allow us to moved the pin pieced 
                        what if we move the king and is in the position of pinned we would still be able to move the pinned piece and let king be in check
                    '''
            else:  # if double check then king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check all checks in moves are fine
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
                # print("checkmate")
            else:
                self.stalemate = True
                # print("stalemate")
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    '''
    # check if the current player is in check
    def inCheck(self):
        # after we moved a piece to prevent from check its still out turn to play,
        # as we changed turn back to us before calling inCheck, to get the king's position to see if king is still under attack
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKinglocation[0], self.whiteKinglocation[1])
        else:
            return self.squareUnderAttack(self.blackKinglocation[0], self.blackKinglocation[1])
    '''

    # check if enemy can attack your king after you make a move while you were in check
    # row, col is the position of the king in attack
    def squareUnderAttack(self, row, col, allyColor):
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:  # no attack from that direction
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # Possibilities
                        # 1) Rook in any orthogonal directions
                        # 2) Bishop in any diagonal
                        # 3) Queen in orthogonal or diagonal directions
                        # 4) Pawn if onw square away in any diagonal
                        # 5) King in any direction to 1 square (to prevent king move controlled by another king)
                        '''
                        For Rook we will check only if directions and up, down, left, right which is in range 0 <= j <=  3 in directions.
                        Similarty for bishop, in directions we have added the bishop direction in directions (4 to 7).
                        For pawn if one forward diagonal square in front of king has opponent's pawn
                        '''
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            return True
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            # traverse every position to find validmove for each piece
            for col in range(len(self.board[0])):
                # check if the piece on the board[row][col] is black or white or empty
                turn = self.board[row][col][0]
                # check if the piece is white and white to move or piece is black and black to move
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    # if the piece is bR(black rook) or wp(white pawn) it returns the second character (R for Rook, Q for Queen, p for Pawn)
                    piece = self.board[row][col][1]
                    # same as (if piece == p (pawn)) -> self.getPawnMoves(row,col,moves)
                    self.moveFunctions[piece](row, col, moves)
        return moves

    # Get all the Pawn moves for the Pawn located at row, col and add it to the moves
    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        moveAmount = -1 if self.whiteToMove else 1
        startRow = 6 if self.whiteToMove else 1
        enemyColor = 'b' if self.whiteToMove else 'w'

        # Single square advance
        if self.board[row + moveAmount][col] == "--":  # first square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, col), (row+moveAmount, col), self.board))
                # Check if pawn can advance two squares
                if row == startRow and self.board[row + 2 * moveAmount][col] == "--":
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))

        # Capturing, including friendly pieces except for the king
        for dCol in [-1, 1]:  # Check diagonal captures
            if 0 <= col + dCol <= 7:
                if not piecePinned or pinDirection == (moveAmount, dCol):
                    endPiece = self.board[row + moveAmount][col + dCol]
                    if endPiece != "--" and endPiece[1] != 'K':
                        moves.append(Move((row, col), (row + moveAmount, col + dCol), self.board))

    # Get all the Rook moves for the Rook located at row, col and add it to the moves
    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':  # Prevent removing Queen's pin
                    self.pins.remove(self.pins[i])
                break

        # Directions the rook can move (down, up, right, left)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for direction in directions:
            for i in range(1, 8):  # Rook can move up to 7 squares
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Stay within board limits
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # Empty square
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        else:
                            # Allow capturing own pieces except the King
                            if endPiece[1] != 'K':  
                                moves.append(Move((row, col), (endRow, endCol), self.board))
                            break  # Can't move past any piece (even your own)
                else:
                    break  # Off the board


    # Get all the Bishop moves for the Bishop located at row, col and add it to the moves
    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]  # diagonals

        for direction in directions:
            for i in range(1, 8):  # The bishop can move up to 7 squares
                endRow = row + direction[0] * i  # destination row
                endCol = col + direction[1] * i  # destination col
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # ensure it's on the board
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty square
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        else:
                            # Allow capturing own pieces except the King
                            if endPiece[1] != 'K':  
                                moves.append(Move((row, col), (endRow, endCol), self.board))
                            break  # Can't move past any piece
                else:
                    break  # Off the board

    # Get all the Knight moves for the Knight located at row, col and add it to the moves
    def getKnightMoves(self, row, col, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        # List of all possible knight moves
        AllPossibleKnightMoves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for m in AllPossibleKnightMoves:
            endRow = row + m[0]  # destination row
            endCol = col + m[1]  # destination col

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # ensure the move is within the board
                if not piecePinned:  # ensure the piece is not pinned
                    endPiece = self.board[endRow][endCol]
                    # Allow capturing own pieces (except king)
                    if endPiece == '--' or endPiece[1] != 'K':
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    # Get all the Queen moves for the Queen located at row, col and add it to the moves
    def getQueenMoves(self, row, col, moves):
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    # Get all the King moves for the King located at row, col and add it to the moves
    def getKingMoves(self, row, col, moves):
        # These loops cover all possible moves for the king (one square in all directions)
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:  # skip the square where the king is
                    continue

                endRow = row + i
                endCol = col + j
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # within the board boundaries
                    endPiece = self.board[endRow][endCol]

                    # Allow the king to move to any square, even if occupied by friendly pieces (except another king)
                    if endPiece == '--' or endPiece[1] != 'K':
                        # Temporarily move the king to check for checks
                        originalLocation = self.whiteKinglocation if self.whiteToMove else self.blackKinglocation
                        if self.whiteToMove:
                            self.whiteKinglocation = (endRow, endCol)
                        else:
                            self.blackKinglocation = (endRow, endCol)

                        # Check if this move puts the king in check
                        inCheck, pins, checks = self.checkForPinsAndChecks()
                        if not inCheck:  # If not in check, the move is valid
                            moves.append(Move((row, col), (endRow, endCol), self.board))

                        # Restore the king's original location
                        if self.whiteToMove:
                            self.whiteKinglocation = originalLocation
                        else:
                            self.blackKinglocation = originalLocation

        # Also handle castling
        self.getcastleMoves(row, col, moves, 'w' if self.whiteToMove else 'b')


    def getcastleMoves(self, row, col, moves, allyColor):
        inCheck = self.squareUnderAttack(row, col, allyColor)
        if inCheck:
            return
        if (self.whiteToMove and self.whiteCastleKingside) or (not self.whiteToMove and self.blackCastleKingside):
            self.getKingsidecastleMoves(row, col, moves, allyColor)
        if (self.whiteToMove and self.whiteCastleQueenside) or (not self.whiteToMove and self.blackCastleQueenside):
            self.getQueensidecastleMoves(row, col, moves, allyColor)

    def getKingsidecastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--" and not self.squareUnderAttack(row, col + 1, allyColor) and not self.squareUnderAttack(row, col + 2, allyColor):
            moves.append(Move((row, col), (row, col + 2),
                         self.board, castle=True))

    def getQueensidecastleMoves(self, row, col, moves, allyColor):
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--" and not self.squareUnderAttack(row, col - 1, allyColor) and not self.squareUnderAttack(row, col - 2, allyColor):
            moves.append(Move((row, col), (row, col - 2),
                         self.board, castle=True))

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKinglocation[0]
            startCol = self.whiteKinglocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKinglocation[0]
            startCol = self.blackKinglocation[1]
        # from king position in all directions, look for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # find if there is a piece
                    endPiece = self.board[endRow][endCol]
                    # if it's your piece it could be pinned by enemy
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # so add it to the possiblePin
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # after that square if there is another of allied piece, no pins or check is possible
                            break
                    elif endPiece[0] == enemyColor:  # if an enemy piece is found
                        type = endPiece[1]
                        # Possibilities
                        # 1) Rook in any orthogonal directions
                        # 2) Bishop in any diagonal
                        # 3) Queen in orthogonal or diagonal directions
                        # 4) Pawn if onw square away in any diagonal
                        # 5) King in any direction to 1 square (to prevent king move controlled by another king)
                        '''
                        For Rook we will check only if directions and up, down, left, right which is in range 0 <= j <=  3 in directions.
                        Similarty for bishop, in directions we have added the bishop direction in directions (4 to 7).
                        For pawn if one forward diagonal square in front of king has opponent's pawn
                        '''
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            '''
                            now check if king is pinned or in check
                            '''
                            if possiblePin == ():  # no ally piece infront of king, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece infront of king but not applying any check
                            break
                else:
                    break  # off board
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def updateCastleRights(self, move):

        if move.pieceMoved == 'wK':
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.blackCastleKingside = False
            self.blackCastleQueenside = False

        # rook captured
        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 0:
            self.whiteCastleQueenside = False
        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 7:
            self.whiteCastleKingside = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 0:
            self.blackCastleQueenside = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 7:
            self.blackCastleKingside = False

    def getBoardString(self):
        # Convert the board state to a string
        boardString = ""
        for row in self.board:
            for square in row:
                boardString += square
        return boardString


class castleRights():
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move():
    # mapping keys to values
    # board[0][0] position in chess board is denoted as a7 (position of Black Rook)

    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {value: key for key, value in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {value: key for key, value in filesToCols.items()}

    pieceNotation = {
        "P": "",
        "R": "R",
        "N": "N",
        "B": "B",
        "Q": "Q",
        "K": "K"
    }

    # add an optional parameter to identify, the square for enpassant
    def __init__(self, startSquare, endSquare, board, isEnpassantMove=False, castle=False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.castle = castle
        if isEnpassantMove == True:
            self.pieceCaptured = board[self.startRow][self.endCol]
        else:
            self.pieceCaptured = board[self.endRow][self.endCol]
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol
        # pawn promotion
        gs = GameState()
        if (gs.playerWantsToPlayAsBlack):
            self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 7) or (
                self.pieceMoved == "bp" and self.endRow == 0)
        else:
            self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (
                self.pieceMoved == "bp" and self.endRow == 7)
        '''
        this is same as 

        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.isPawnPromotion = True

        '''
        # en passant
        self.isEnpassantMove = isEnpassantMove

    # overriding the equals method (tell python if two moves are equal)
    # no two pieces should be on the same square
    # start pos and end pos can't be same

    def __eq__(self, other):  # comparing object with another object saved in other
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getPieceNotation(self.pieceMoved, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

    def getPieceNotation(self, piece, col):
        if piece[1] == 'p':
            return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        return self.pieceNotation[piece[1]] + self.colsToFiles[col]

    # overriding the str() function
    def __str__(self):
        # castle move:
        if self.castle:
            return "O-O" if self.endCol == 6 else "O-O-O"

        startSquare = self.getRankFile(self.startRow, self.startCol)
        endSquare = self.getRankFile(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return startSquare + "x" + endSquare
            else:
                return startSquare+endSquare

        # pawn promotion (add later)
        # add + for check # for checkmate

        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            return moveString + self.colsToFiles[self.startCol] + "x" + endSquare
        return moveString + self.colsToFiles[self.startCol] + endSquare
