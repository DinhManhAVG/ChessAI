import random

piece_score = {
    "K": 0,
    "Q": 10,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1,
}

# Mảng này dùng để đánh giá vị trí của quân cờ trên bàn cờ để ưu tiên quân cờ đi vào vị trí có điểm cao hơn
knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1]}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

# Random move
def find_random_move(valid_moves):
    print("random_move")
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

# Greedy algorithm
def score_material(board):
    """
    Ví dụ: Tới lượt trắng có thể ăn quân tượng hoặc xe của đối phương thì sẽ ưu tiên ăn quân xe vì điểm số của quân xe cao hơn
    Do đó sẽ ưu tiên ăn các quân đen có piece_score để tránh bị giảm giá trị score của bàn cờ và giúp tối ưu nước đi cho quân trắng
    =================================================================================================================
    Ngược lại với lượt đi quân đen, nó cũng sẽ ưu tiên ăn các quân có điểm cao để lúc tính giá trị bàn cờ thì các quân có điểm cao đã bị ăn
    nên score của bàn cờ sẽ giảm đi và giúp tối ưu nước đi cho quân đen
    """
    score = 0

    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score
    return score

# find_best_move sử dụng minimax với 2 tầng
def find_best_move(gs, valid_moves):
    print("find_best_move")
    turn_multiplier = 1 if gs.whiteToMove else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.makeMove(player_move)
        opponent_moves = gs.getValidMoves_2()
        if gs.staleMate:
            opponent_max_score = STALEMATE
        elif gs.checkMate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                gs.makeMove(opponent_move)
                # Sau khi thực hiện nước đi thì gọi hàm này để kiểm tra xem có chiếu tướng hay bế tắc không
                gs.getValidMoves_2()
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
    return  best_player_move

def find_best_move_minimax_without_ab(gs, valid_moves, return_queue):
    """
    Phương pháp giúp gọi đệ quy lần đầu tiên
    """
    print("find_best_move_minimax without alpha beta")
    global next_move, moving_count
    next_move = None
    moving_count = 0

    find_move_minimax(gs, valid_moves, DEPTH, gs.whiteToMove,0, 0)
    return_queue.put(next_move)
    print("Moving count: ", moving_count)
    return next_move


def find_best_move_minimax(gs, valid_moves, return_queue):
    """
    Tối ưu nước đi cho quân đen_AI (vì khi đến nước quân đen thì sẽ gọi hàm này)
    """
    global next_move, moving_count
    next_move = None
    alpha = -CHECKMATE
    beta = CHECKMATE
    
    moving_count = 0

    find_move_minimax(gs, valid_moves, DEPTH, gs.whiteToMove, alpha, beta, is_apply_alpha_beta=True)
    print("Moving count: ", moving_count)
    return_queue.put(next_move)

def find_move_minimax(gs, valid_moves, depth, white_to_move, alpha, beta, is_apply_alpha_beta=False):
    global next_move, moving_count
    moving_count += 1
    if depth == 0:
        return score_material(gs.board)
    
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.makeMove(move)
            next_moves = gs.getValidMoves_2()
            score = find_move_minimax(gs, next_moves, depth - 1, False, alpha, beta, is_apply_alpha_beta)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undoMove()

            if is_apply_alpha_beta:
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # beta cut-off
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.makeMove(move)
            next_moves = gs.getValidMoves_2()
            score = find_move_minimax(gs, next_moves, depth - 1, True, alpha, beta, is_apply_alpha_beta)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undoMove()
            if is_apply_alpha_beta:
                beta = min(beta, score)
                if beta <= alpha:
                    break  # alpha cut-off
        return min_score