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

        self.whiteToMove = True

        # Ghi lại nhật kí di chuyển
        self.moveLog: List[Move] = []

    def makeMove(self, move: "Move") -> None:
        self.board[move.startRow][move.startColumn] = "--"
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove # Chuyển lượt chơi


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
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startColumn) + self.get_rank_file(
            self.endRow, self.endColumn
        )

    def get_rank_file(self, row, column) -> str:
        """
        Ví dụ truyền vào 0,1 => Output: B8
        """
        return self.colsToFiles[column] + self.rowsToRanks[row]
