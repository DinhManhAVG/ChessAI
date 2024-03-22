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
        self.moveFunctions = { 'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                               'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True

        # Ghi lại nhật kí di chuyển
        self.moveLog: List[Move] = []


    def makeMove(self, move: "Move") -> None:
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove # Chuyển lượt chơi

    def undoMove(self):
        if len(self.moveLog) != 0: # Đã di chuyển nước cờ rồi
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn] = move.pieceMoved
            self.board[move.endRow][move.endColumn] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Đổi lượt chơi

    def getValidMoves(self):
        return self.getAllPossibleMoves()
    
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
            if col+1 <= 7: # Di Chuyển về  bên phải
                if self.board[row - 1][col + 1][0] == 'b': # Ăn quân đen bên phải
                    moves.append(Move((row, col), (row-1, col+1), self.board))
        else:
            if self.board[row + 1][col] == "--": # Con tốt đi xuống 1 nước
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--": # Con tốt đi xuống 2 nước
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0: # Di Chuyển về  bên trái
                if self.board[row + 1][col - 1][0] == 'w': # Ăn quân đen bên trái
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7: # Di Chuyển về  bên phải
                if self.board[row + 1][col + 1][0] == 'w': # Ăn quân đen bên phải
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))

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

class Move:
    # Cờ vua ví dụ ô B8 thì đưa ra vị trí trong board có rowIndex = 0, column index = 1
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {value: key for key, value in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {value: key for key, value in filesToCols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.startRow = start_sq[0]
        self.startColumn = start_sq[1]
        self.endRow = end_sq[0]
        self.endColumn = end_sq[1]
        # pieceMoved là quân cờ được đánh (vị trí ban đầu) còn pieceCaptured là quân cờ ở vị trí đích
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]
        self.moveID = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn
        # print(self.moveID)
    
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
