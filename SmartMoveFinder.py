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
DEPTH = 2

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

def score_board(gs):
    """
    Điểm dương tốt cho trắng và điểm âm tốt cho đen
    """
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE # Black wins
        else:
            return CHECKMATE # White wins
    elif gs.staleMate:
        return STALEMATE
    
    return score_material(gs.board)

def find_best_move(gs, valid_moves):
    print("find_best_move")
    turn_multiplier = 1 if gs.whiteToMove else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.makeMove(player_move)
        opponent_moves = gs.getValidMoves()
        if gs.staleMate:
            opponent_max_score = STALEMATE
        elif gs.checkMate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                gs.makeMove(opponent_move)
                # Sau khi thực hiện nước đi thì gọi hàm này để kiểm tra xem có chiếu tướng hay bế tắc không
                gs.getValidMoves()
                if gs.checkMate:
                    score = CHECKMATE
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

def find_best_move_minimax(gs, valid_moves):
    """
    Phương pháp giúp gọi đệ quy lần đầu tiên
    """
    print("find_best_move_minimax")
    global next_move
    next_move = None

    find_move_minimax(gs, valid_moves, DEPTH, gs.whiteToMove)
    return next_move

def find_move_minimax(gs, valid_moves, depth, white_to_move):
    print("find_move_minimax")
    global next_move
    if depth == 0:
        return score_material(gs.board)
    
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.makeMove(move)
            score = find_move_minimax(gs, gs.getValidMoves(), depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undoMove()
        return max_score
        
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.makeMove(move)
            score = find_move_minimax(gs, gs.getValidMoves(), depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undoMove()
        return min_score
    