import pygame as py
import ChessEngine, SmartMoveFinder as smd
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512
DIMENSION = 8

# Kích thước 1 ô
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


# Initialize
def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = py.transform.scale(
            py.image.load(f"images/{piece}.png"), size=(SQ_SIZE, SQ_SIZE)
        )


def main():
    py.init()
    py.mixer.init()

    screen = py.display.set_mode(size=(WIDTH, HEIGHT))
    py.display.set_caption("Chess AI")

    # Màn hình game
    clock = py.time.Clock()
    screen.fill(py.Color("white"))

    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves_2()
    move_made = False # Biến cờ trạng thái khi thực hiện 1 nước đi
    animate = False # Biến cờ trạng thái khi thực hiện animation

    load_images()

    running = True
    sq_selected = ()  # Lưu trữ click cuối cùng of người chơi
    player_clicks = []  # Lưu giữ click của người dùng (click đầu, và cuối khi chọn 1 ô)
    game_over = False

    # player_one là người chơi quân trắng và player_two là người chơi quân đen
    # Nếu cái nào là False thì là AI chơi còn True là người chơi
    player_one = True  # Nếu chơi với AI, player_one = True, ngược lại player_one = False
    player_two = False  # Nếu chơi với AI, player_two = True, ngược lại player_two = False
    ai_thinking = False
    move_finder_process = None # Process để tìm nước đi tốt nhất cho AI
    move_undone = False

    move_sound = py.mixer.Sound('./audio/move-self.mp3')
    capture_sound = py.mixer.Sound('./audio/capture.mp3')

    while running:
        human_turn = (game_state.whiteToMove and player_one) or (not game_state.whiteToMove and player_two)
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = py.mouse.get_pos()

                    # Do trục X nằm ngang => Tìm index của column, row
                    column = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sq_selected == (row, column):
                        # Người chơi đã click 2 lần vào 1 ô, tiến hành clear
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, column)
                        player_clicks.append(sq_selected)
                    
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(
                            player_clicks[0], player_clicks[1], game_state.board
                        )
                        print(move.getChessNotation())

                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                if move.pieceCaptured != "--" or (move.endRow, move.endColumn) == game_state.enPassantPossible:
                                    capture_sound.play()
                                else:
                                    move_sound.play()
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]

            # Xử lý event key handlers
            elif event.type == py.KEYDOWN:
                # Nhấn phím Z
                if event.mod & py.KMOD_CTRL and event.key == py.K_z:
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if event.key == py.K_r: # Nhấn phím R để reset game
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves_2()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
        
        # AI move finder
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                print("AI is thinking...")
                return_queue = Queue() # Sử dụng Queue để truyền dữ liệu giữa các process
                # move_finder_process = Process(target=smd.find_best_move_minimax_without_ab, args=(game_state, valid_moves, return_queue))
                move_finder_process = Process(target=smd.find_best_move_minimax, args=(game_state, valid_moves, return_queue))
                move_finder_process.start() # Bắt đầu process goi hàm find_best_move_minimax
            
            if not move_finder_process.is_alive(): # Kiểm tra xem process đã kết thúc chưa
                print("AI move found")
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = smd.find_random_move(valid_moves)
                if ai_move.pieceCaptured != "--" or (ai_move.endRow, ai_move.endColumn) == game_state.enPassantPossible:
                    capture_sound.play()
                else:
                    move_sound.play()
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animate_move(game_state.moveLog[-1], screen, game_state, clock)
            valid_moves = game_state.getValidMoves_2()
            move_made = False
            animate = False
            move_undone = False

        draw_game_state(screen, game_state, valid_moves, sq_selected)

        if game_state.checkMate:
            game_over = True
            if game_state.whiteToMove:
                draw_text(screen, "Black wins by checkmate")
            else:
                draw_text(screen, "White wins by checkmate")
        elif game_state.staleMate:
            game_over = True
            string_win = "Black wins by stalemate" if game_state.whiteToMove else "White wins by stalemate"
            draw_text(screen, string_win)

        # Điều chỉnh tốc độ của khung hinh
        # Đảm bảo rằng mỗi lần vòng lặp thực hiện, thời gian giữa các khung hình liên tiếp sẽ ít nhất là 1/MAX_FPS giây.
        clock.tick(MAX_FPS)

        # Cập nhật lại màn hình
        py.display.flip()


def highlight_squares(screen, game_state, valid_moves, sq_selected):
    """
    Highlight ô đã chọn và các ô có thể di chuyển
    """
    if sq_selected != ():
        row, column = sq_selected
        if game_state.board[row][column][0] == ("w" if game_state.whiteToMove else "b"):
            # Vẽ hình chữ nhật xanh lá cây cho ô đã chọn
            s = py.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Độ trong suốt
            s.fill(py.Color("blue"))
            screen.blit(s, (column * SQ_SIZE, row * SQ_SIZE))
            # Vẽ các nước đi hợp lệ
            s.fill(py.Color("yellow"))
            for move in valid_moves:
                if move.startRow == row and move.startColumn == column:
                    screen.blit(
                        s, (move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE)
                    )

def highlight_in_check_king(screen, game_state):
    # Tô cảnh báo màu đỏ cho quân vua trên bàn cờ đội địch nếu bị đang inCheck
    if game_state.inCheck:
        if game_state.whiteToMove:
            # Highlight màu đỏ tại quân vua của đội trắng
            white_king_location = game_state.whiteKingLocation
            s = py.Surface((SQ_SIZE, SQ_SIZE), py.SRCALPHA)
            s.fill(py.Color(255, 0, 0, 100))
            screen.blit(s, (white_king_location[1] * SQ_SIZE, white_king_location[0] * SQ_SIZE))
            screen.blit(IMAGES["wK"], (white_king_location[1] * SQ_SIZE, white_king_location[0] * SQ_SIZE))
        else:
            # Highlight màu đỏ tại quân vua của đội đen
            black_king_location = game_state.blackKingLocation
            s = py.Surface((SQ_SIZE, SQ_SIZE), py.SRCALPHA)
            s.fill(py.Color(255, 0, 0, 100))
            screen.blit(s, (black_king_location[1] * SQ_SIZE, black_king_location[0] * SQ_SIZE))
            screen.blit(IMAGES["bK"], (black_king_location[1] * SQ_SIZE, black_king_location[0] * SQ_SIZE))

def animate_move(move, screen, game_state, clock):
    global colors
    delta_row = move.endRow - move.startRow
    delta_column = move.endColumn - move.startColumn
    frames_per_square = 10  # Frames để di chuyển 1 ô
    frame_count = (abs(delta_row) + abs(delta_column)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.startRow + delta_row * frame / frame_count, move.startColumn + delta_column * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, game_state.board)
        # Xóa quân cờ tại ô cũ
        color = colors[(move.endRow + move.endColumn) % 2]
        end_square = py.Rect(move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        py.draw.rect(screen, color, end_square)
        # Vẽ quân cờ tại ô mới
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], end_square)
        
        # Vẽ quân cờ di chuyển
        screen.blit(IMAGES[move.pieceMoved], py.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        py.display.flip()
        clock.tick(120)

def draw_text(screen, text):
    font = py.font.SysFont("Helvitca", 50, True, False)
    text_object = font.render(text, 0, py.Color("Gray"))
    text_location = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2, HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, py.Color("Black"))
    screen.blit(text_object, text_location.move(2, 2))

def draw_board(screen):
    """
    Vẽ các hình vuông cho bàn cờ,
    """
    global colors
    colors = [py.Color("#ebecd0"), py.Color("#739552")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row + column) % 2]
            py.draw.rect(
                screen,
                color,
                py.Rect(
                    column * SQ_SIZE,
                    row * SQ_SIZE,
                    SQ_SIZE,
                    SQ_SIZE,
                ),
            )


def draw_pieces(screen, board):
    """
    board: Ma trận chứa các quân cờ
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]

            # Ô trống
            if piece != "--":
                # Vẽ một hình ảnh lên một bề mặt
                screen.blit(
                    IMAGES[piece],
                    # Định nghĩa HCN có các tham số left, top, width, height
                    py.Rect(
                        column * SQ_SIZE,
                        row * SQ_SIZE,
                        SQ_SIZE,
                        SQ_SIZE,
                    ),
                )


def draw_game_state(screen, game_state, valid_moves, sq_selected):
    draw_board(screen)  # Vẽ bàn cờ
    draw_pieces(screen, game_state.board)  # Vẽ các quân cờ vào
    highlight_squares(screen, game_state, valid_moves, sq_selected)  # Vẽ ô đã chọn và các ô có thể di chuyển
    highlight_in_check_king(screen, game_state)  # Highlight quân vua nếu bị chiếu

if __name__ == "__main__":
    main()