import random

piece_score = {
    "K": 0,
    "Q": 10,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1,
}
CHECKMATE = 1000
STALEMATE = 0

# Random move
def find_random_move(valid_moves):
    print("random_move")
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

# Greedy algorithm
def score_material(board):
    """
    Score the material on the board
    Ví dụ: Tới lượt trắng có thể ăn quân tượng hoặc xe của đối phương thì 
    sẽ ưu tiên ăn quân xe vì điểm số của quân xe cao hơn
    """
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]
    return score


def find_best_move(gs, valid_moves):
    print("find_best_move")
    turn_multiplier = 1 if gs.whiteToMove else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.makeMove(player_move)
        opponent_moves = gs.getValidMoves()
        opponent_max_score = -CHECKMATE
        for opponent_move in opponent_moves:
            gs.makeMove(opponent_move)
            if gs.checkMate:
                score = -turn_multiplier * CHECKMATE
            elif gs.staleMate:
                score = STALEMATE
            else:
                score = -turn_multiplier * score_material(gs.board)
            if score > opponent_max_score:
                opponent_max_score = score
            gs.undoMove()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gs.undoMove()
    return best_player_move
