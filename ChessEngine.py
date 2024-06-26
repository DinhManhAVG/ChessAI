from typing import List


class GameState:
    def __init__(self):
        # Tạo BàN cờ 8x8
        # Kí tự đầu là màu, kí tự sau là tên quân cờ
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = { 'p': self.getPawnMoves_2, 'R': self.getRookMoves_2, 'N': self.getKnightMoves_2,
                               'B': self.getBishopMoves_2, 'Q': self.getQueenMoves_2, 'K': self.getKingMoves_2}

        self.whiteToMove = True

        # Ghi lại nhật kí di chuyển
        self.moveLog: List[Move] = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False # Bị chiếu tướng
        self.staleMate = False # staleMate là khi không còn nước đi hợp lệ nào

        ### Advanced algorithm
        # Kiểm tra xem vua có bị tấn công không
        self.inCheck = False

        # pins là danh sách các quân đang bị chặn
        self.pins = []

        # checks là danh sách các quân đang tấn công vua
        self.checks = []
        self.enPassantPossible = () # Ô mà quân tốt có thể ăn quân tốt đối phương
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]


    def makeMove(self, move: "Move") -> None:
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove # Chuyển lượt chơi
        # Cập nhật lại vị trí quân vua khi di chuyển
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endColumn)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endColumn)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + 'Q'

        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endColumn] = "--" #capturing the pawn

        # Cập nhật lại vị trí quân tốt đối phương
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # Chỉ khi con tốt di chuyển 2 ô ở vị trí ban đầu
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startColumn)
        else:
            self.enPassantPossible = ()

        # castling move
        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2: # kingside castle move
                self.board[move.endRow][move.endColumn - 1] = self.board[move.endRow][move.endColumn + 1] # Di chuyển xe
                self.board[move.endRow][move.endColumn + 1] = "--" # Xóa quân xe ở vị trí cũ
            else: # queenside castle move
                self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                self.board[move.endRow][move.endColumn - 2] = "--"

        self.enPassantPossibleLog.append(self.enPassantPossible)


        # Cập nhật castling rights - Bất kể khi nào vua hoặc xe di chuyển
        self.updateCastlingRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0: # Đã di chuyển nước cờ rồi
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Đổi lượt chơi
            
            # Cập nhật lại vị trí quân vua khi di chuyển
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startColumn)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startColumn)
            # undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endColumn] = "--" # Đặt lại ô trống
                self.board[move.startRow][move.endColumn] = move.pieceCaptured
                # TODO
                # self.enPassantPossible = (move.endRow, move.endColumn)
            # undo 2 ô di chuyển của con tốt
            # if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                # self.enPassantPossible = ()
            
            # Adding
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
            
            # undo a castling move
            self.castleRightsLog.pop() # Loại bỏ quyền castling cuối cùng
            newRights = self.castleRightsLog[-1] # Lấy quyền castling trước đó
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            #undo castle move
            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2: # kingside
                    self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 1]
                    self.board[move.endRow][move.endColumn - 1] = "--"
                else: # queenside
                    self.board[move.endRow][move.endColumn - 2] = self.board[move.endRow][move.endColumn + 1]
                    self.board[move.endRow][move.endColumn + 1] = "--"

            self.checkMate = False
            self.staleMate = False

    def updateCastlingRights(self, move):
        """
        Cập nhật lại quyền di chuyển của vua và xe
        """ 
        # Khi vua hoặc xe di chuyển khỏi vị trí ban đầu mà không di chuyển vào vị trí castling thì mất quyền castling
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startColumn == 0: # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startColumn == 7: # right rook
                    self.currentCastlingRight.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startColumn == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startColumn == 7:
                    self.currentCastlingRight.bks = False
            
    def getValidMoves(self):
        temp_enpassant_possible = self.enPassantPossible
        temp_castle_rights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # Sinh ra tất cả nước đi có thể
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # Mỗi nước đi, tạo ra các nước đi
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # Tạo ra tất cả các nước đi của đối thủ

            # Mỗi nước đi đối thủ, nếu họ tấn công vua
            self.whiteToMove = not self.whiteToMove
            if self.inCheckFunction():
                moves.remove(moves[i]) # Nếu họ có thể tấn công vua thì nước đi đó không hợp lệ
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # Không có nước đi hợp lệ nào
            if self.inCheckFunction():
                self.checkMate = True
                print("Check mate")
            else:
                self.staleMate = True
                print("End game")
        else:
            self.checkMate = False
            self.staleMate = False
        self.enPassantPossible = temp_enpassant_possible
        self.currentCastlingRight = temp_castle_rights
        return moves

    def inCheckFunction(self):
        """
        Xác định người chơi hiện tại đang được check
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    def squareUnderAttack(self, row, col) -> bool:
        """
        Xác định kẻ địch có thể tấn công ô (row, col) không
        """
        self.whiteToMove = not self.whiteToMove # Đổi lượt cho đối thủ đánh thử xem có ăn được quân vua không nghĩa là ô rơw col đang kiểm tra
        opp_moves: List[Move] = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opp_moves:
            if move.endRow == row and move.endColumn == col: # Ô vuông bị tấn công
                return True;
        return False        
        

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                # Lấy ra màu của quân cờ
                turn = self.board[row][col][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)
        return moves
    
    def getPawnMoves(self, row, col, moves):
        """
        Lấy tất cả nước đi của con tốt
        """
        if self.whiteToMove:
            if self.board[row - 1][col] == "--": # Con tốt đi lên 1 nước
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--": # Con tốt đi lên 2 nước
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col-1 >= 0: # Di Chuyển về  bên trái
                if self.board[row - 1][col - 1][0] == 'b': # Ăn quân đen bên trái
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row - 1, col - 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row-1, col-1), self.board, isEnpassantMove = True))
            if col+1 <= 7: # Di Chuyển về  bên phải
                if self.board[row - 1][col + 1][0] == 'b': # Ăn quân đen bên phải
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row - 1, col + 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row-1, col+1), self.board, isEnpassantMove = True))
        else:
            if self.board[row + 1][col] == "--": # Con tốt đi xuống 1 nước
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--": # Con tốt đi xuống 2 nước
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0: # Di Chuyển về  bên trái
                if self.board[row + 1][col - 1][0] == 'w': # Ăn quân đen bên trái
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove = True))
            if col + 1 <= 7: # Di Chuyển về  bên phải
                if self.board[row + 1][col + 1][0] == 'w': # Ăn quân đen bên phải
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove = True))

    def getRookMoves(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân xe
        """
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for index in range(1, 8):
                end_row = row + direction[0] * index
                end_col = col + direction[1] * index
                if 0 <= end_row < 8 and 0 <= end_col < 8: # Vẫn nằm trên bảng
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--": # Ô trống
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color: # Có quân địch trên đường đi
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else: # Quân mình
                        break
                else: # Ngoài bảng
                    break
    
    def getKnightMoves(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân mã
        """
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        # Màu quân đồng minh
        ally_color = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                end_piece = self.board[endRow][endCol]
                if end_piece[0] != ally_color: # Không phải quân đồng minh (Quân địch hoặc ô trống)
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân tượng
        """
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for index in range(1, 8):
                end_row = row + direction[0] * index
                end_col = col + direction[1] * index
                if 0 <= end_row < 8 and 0 <= end_col < 8: # Vẫn nằm trên bảng
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--": # Ô trống
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color: # Có quân địch trên đường đi
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    else: # Quân mình
                        break
                else: # Ngoài bảng
                    break

    def getQueenMoves(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân hậu
        """
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân vua
        """
        # Di chuyển 8 hướng xung quanh nó 1 bước
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        # Màu quân đồng minh
        ally_color = "w" if self.whiteToMove else "b"
        for index in range(8):
            end_row = row + king_moves[index][0]
            end_col = col + king_moves[index][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # Không phải quân đồng minh (Quân địch hoặc ô trống)
                    moves.append(Move((row, col), (end_row, end_col), self.board))
    
    def getCastleMoves(self, row, col, moves):
        """
        Lấy nước đi của quân vua khi castling
        """
        if self.squareUnderAttack(row, col):
            return # Không thể castling khi vua đang bị chiếu
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        """
        Đi nước đi castling về phía quân vua
        """
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove = True))

    def getQueensideCastleMoves(self, row, col, moves):
        """
        Đi nước đi castling về phía quân hậu
        """
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove = True))

    # Advanced algorithm

    def getValidMoves_2(self):
        temp_castle_rights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                          self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # Sinh ra tất cả nước đi có thể
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            king_row = self.whiteKingLocation[0]
            king_col = self.whiteKingLocation[1]
        else:
            king_row = self.blackKingLocation[0]
            king_col = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: # Chỉ có 1 quân tấn công vua
                moves = self.getAllPossibleMoves()

                # Lấy quân cờ đầu tiên (có duy nhất 1 quân) đe dọa vua
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = [] # Các ô có thể di chuyển để chặn quân tấn công
                if piece_checking[1] == 'N': # Nếu quân tấn công là quân mã thì không thể chặn được
                    valid_squares = [(check_row, check_col)]
                else:
                    # 
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        # Kiểm tra xem ô hợp lệ hiện tại có phải là vị trí của quân cờ đang đe dọa vua không. 
                        # Nếu đúng, thì dừng vòng lặp vì không cần phải kiểm tra các ô sau nữa.
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        # Nếu nước đi không chặn đường tấn công thì xóa nước đi đó, chỉ giữ lại nước chặn đường tấn công
                        # Ví dụ con tốt trắng có thể ăn con hậu đối phương, nhưng nếu đi nước này thì quân đen sẽ ăn vua, do đó
                        # nước đi này không hợp lệ, và sẽ xóa nó đi khỏi các nước đi hợp lệ
                        if not (moves[i].endRow, moves[i].endColumn) in valid_squares:
                            moves.remove(moves[i])
            else:
                # Nếu có 2 quân tấn công vua thì vua phải di chuyển mới tránh bị chiếu
                self.getKingMoves(king_row, king_col, moves) # Không thể chặn được nếu có 2 quân tấn công => vua phải di chuyển
        else:
            # Nếu không bị chiếu thì tất cả các nước đi hợp lệ
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0: # Không có nước đi hợp lệ nào
            if self.inCheck:
                self.checkMate = True
                print("Check mate")
            else:
                self.staleMate = True
                print("End game")
        else:
            self.checkMate = False
            self.staleMate = False
        self.currentCastlingRight = temp_castle_rights
        return moves

    def checkForPinsAndChecks(self):
        """
        Xác định xem vua có bị chiếu không và các quân cờ đang bị chặn
        """
        pins = []
        checks = []
        in_check = False
        if self.whiteToMove:
            enemy_color = 'b'
            ally_color = 'w'
            # Vị trí của quân vua
            start_row = self.whiteKingLocation[0]
            start_col = self.whiteKingLocation[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.blackKingLocation[0]
            start_col = self.blackKingLocation[1]
        
        # directions là 8 hướng xung quanh vua
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            d = directions[i]
            possible_pin = () # Chứa các quân cờ có thể chặn địch tấn công vua
            # j là khoảng cách các quân cờ với quân vua đang xét
            for j in range(1, 8):
                end_row = start_row + d[0] * j
                end_col = start_col + d[1] * j
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]

                    # Nếu màu quân cờ đang xét là màu đồng minh
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():
                            # Xác định vị trí quân đồng minh và hướng tấn công của quân địch
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            # Nếu đã có quân cờ chặn rồi thì không cần xét nữa, đi xét hướng khác
                            break
                    elif end_piece[0] == enemy_color:
                        # Xác định loại quân cờ đang tấn công
                        type_piece = end_piece[1]

                        # 0 <= i <= 3 là các hướng đi ngang dọc, 4 <= i <= 7 là các hướng đi chéo
                        # Hướng của (i, j) trong directions là xét theo chỉ số trong ma trận 8x8 với thứ tự row, col
                        # Với trường hợp con tốt, quân địch tấn công từ 2 hướng chéo với 6 <= i <= 7 và địch màu trắng w thì nghĩa là quân tốt đen đang tấn công vua trắng
                        if (0 <= i <= 3 and type_piece == 'R') or \
                                (4 <= i <= 7 and type_piece == 'B') or \
                                (j == 1 and type_piece == 'p' and ((enemy_color == 'w' and 6 <= i <= 7) or \
                                    (enemy_color == 'b' and 4 <= i <= 5))) or \
                                (type_piece == 'Q') or (j == 1 and type_piece == 'K'):
                            if possible_pin == ():
                                # Chưa có quân chặn nên vua đang bị chiếu
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                # Có quân chặn rồi thì thêm vào danh sách các quân chặn
                                pins.append(possible_pin)
                                break
                        else:
                            break

        # Kiểm tra xem quân mã có thể tấn công vua không
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    # Nếu quân mã tấn công vua thì vua đang bị chiếu
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks

    def getPawnMoves_2(self, row, col, moves):
        """
        Lấy tất cả nước đi của con tốt
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[row - 1][col] == "--": # Con tốt đi lên 1 nước
                # Nếu không là quân chặn hoặc là quân chặn nhưng chặn theo hướng dọc thì việc di chuyển là hợp lệ
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    if row == 6 and self.board[row - 2][col] == "--": # Con tốt đi lên 2 nước
                        moves.append(Move((row, col), (row - 2, col), self.board))
            if col-1 >= 0: # Di Chuyển về  bên trái
                if self.board[row - 1][col - 1][0] == 'b': # Ăn quân đen bên trái
                    # Nếu không là quân chặn hoặc là quân chặn nhưng chặn theo hướng chéo trái thì việc di chuyển theo hướng chéo trái là hợp lệ
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, col), (row-1, col-1), self.board))
                    elif (row - 1, col - 1) == self.enPassantPossible:
                        moves.append(Move((row, col), (row-1, col-1), self.board, isEnpassantMove = True))
            if col+1 <= 7: # Di Chuyển về hướng chéo bên phải
                if self.board[row - 1][col + 1][0] == 'b': # Ăn quân đen bên phải
                    # Nếu không là quân chặn hoặc là quân chặn nhưng chặn theo hướng chéo phải thì việc di chuyển theo hướng chéo phải là hợp lệ
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, col), (row-1, col+1), self.board))
                    elif (row - 1, col + 1) == self.enPassantPossible:
                        moves.append(Move((row, col), (row-1, col+1), self.board, isEnpassantMove = True))
        else:
            if self.board[row + 1][col] == "--": # Con tốt đi xuống 1 nước
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    if row == 1 and self.board[row + 2][col] == "--": # Con tốt đi xuống 2 nước
                        moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0: # Di Chuyển về  bên trái
                if self.board[row + 1][col - 1][0] == 'w': # Ăn quân đen bên trái
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, col), (row + 1, col - 1), self.board))
                    elif (row + 1, col - 1) == self.enPassantPossible:
                        moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove = True))
            if col + 1 <= 7: # Di Chuyển về  bên phải
                if self.board[row + 1][col + 1][0] == 'w': # Ăn quân đen bên phải
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, col), (row + 1, col + 1), self.board))
                    elif (row + 1, col + 1) == self.enPassantPossible:
                        moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove = True))

    def getRookMoves_2(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân xe
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': # Nếu quân bị chặn không phải là quân hậu thì không thể di chuyển
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for index in range(1, 8):
                end_row = row + direction[0] * index
                end_col = col + direction[1] * index
                if 0 <= end_row < 8 and 0 <= end_col < 8: # Vẫn nằm trên bảng
                    # Nếu không bị chặn hoặc bị chặn nhưng di chuyển trên hướng chặn thì việc di chuyển là hợp lệ
                    if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # Ô trống
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # Có quân địch trên đường đi
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else: # Quân mình
                            break
                else: # Ngoài bảng
                    break
    
    def getKnightMoves_2(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân mã
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        # Màu quân đồng minh
        ally_color = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piece_pinned:
                    end_piece = self.board[endRow][endCol]
                    if end_piece[0] != ally_color: # Không phải quân đồng minh (Quân địch hoặc ô trống)
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves_2(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân tượng
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for index in range(1, 8):
                end_row = row + direction[0] * index
                end_col = col + direction[1] * index
                if 0 <= end_row < 8 and 0 <= end_col < 8: # Vẫn nằm trên bảng
                    if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # Ô trống
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # Có quân địch trên đường đi
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else: # Quân mình
                            break
                else: # Ngoài bảng
                    break

    def getQueenMoves_2(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân hậu
        """
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves_2(self, row, col, moves):
        """
        Lấy tất cả nước đi của quân vua
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for index in range(8):
            end_row = row + row_moves[index]
            end_col = col + col_moves[index]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # Không phải quân đồng minh (Quân địch hoặc ô trống)
                    if ally_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally_color == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

class Move:
    # Cờ vua ví dụ ô B8 thì đưa ra vị trí trong board có rowIndex = 0, column index = 1
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {value: key for key, value in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {value: key for key, value in filesToCols.items()}

    def __init__(self, start_sq, end_sq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = start_sq[0]
        self.startColumn = start_sq[1]
        self.endRow = end_sq[0]
        self.endColumn = end_sq[1]
        # pieceMoved là quân cờ được đánh (vị trí ban đầu) còn pieceCaptured là quân cờ ở vị trí đích
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]
        self.moveID = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn
        # parn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # castle move
        self.isCastleMove = isCastleMove

    def __eq__(self, other: object) -> bool:
        """
        Overriding the equals method
        """
        if isinstance(other, Move):
            return  self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startColumn) + self.getRankFile(
            self.endRow, self.endColumn
        )

    def getRankFile(self, row, column) -> str:
        """
        Ví dụ truyền vào 0,1 => Output: B8
        """
        return self.colsToFiles[column] + self.rowsToRanks[row]

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs