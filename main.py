import pygame as p
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
        IMAGES[piece] = p.transform.scale(
            p.image.load(f"images/{piece}.png"), size=(SQ_SIZE, SQ_SIZE)
        )


def main():
    p.init()
    p.mixer.init()

    screen = p.display.set_mode(size=(WIDTH, HEIGHT))
    p.display.set_caption("Chess AI")

    # Màn hình game
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves_2()
    move_made = False # Biến cờ trạng thái khi thực hiện 1 nước đi
    animate = False # Biến cờ trạng thái khi thực hiện animation

    load_images()

    running = True
    sq_selected = ()  # Lưu trữ click cuối cùng of người chơi
    player_clicks = []  # Lưu giữ click của người dùng (click đầu, và cuối khi chọn 1 ô)
    game_over = False

    # playerOne là người chơi quân trắng và playerTwo là người chơi quân đen
    # Nếu cái nào là False thì là AI chơi còn True là người chơi
    playerOne = True  # Nếu chơi với AI, playerOne = True, ngược lại playerOne = False
    playerTwo = False  # Nếu chơi với AI, playerTwo = True, ngược lại playerTwo = False
    AIThinking = False
    moveFinderProcess = None # Process để tìm nước đi tốt nhất cho AI
    moveUndone = False

    move_sound = p.mixer.Sound('./audio/move-self.mp3')
    capture_sound = p.mixer.Sound('./audio/capture.mp3')

    while running:
        human_turn = (game_state.whiteToMove and playerOne) or (not game_state.whiteToMove and playerTwo)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()

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
            elif event.type == p.KEYDOWN:
                # Nhấn phím Z
                if event.mod & p.KMOD_CTRL and event.key == p.K_z:
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if event.key == p.K_r: # Nhấn phím R để reset game
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves_2()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
        
        # AI move finder
        if not game_over and not human_turn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("AI is thinking...")
                returnQueue = Queue() # Sử dụng Queue để truyền dữ liệu giữa các process
                # moveFinderProcess = Process(target=smd.find_best_move_minimax_without_ab, args=(game_state, valid_moves, returnQueue))
                moveFinderProcess = Process(target=smd.find_best_move_minimax, args=(game_state, valid_moves, returnQueue))
                moveFinderProcess.start() # Bắt đầu process goi hàm find_best_move_minimax
            
            if not moveFinderProcess.is_alive(): # Kiểm tra xem process đã kết thúc chưa
                print("AI move found")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = smd.find_random_move(valid_moves)
                if AIMove.pieceCaptured != "--" or (AIMove.endRow, AIMove.endColumn) == game_state.enPassantPossible:
                    capture_sound.play()
                else:
                    move_sound.play()
                game_state.makeMove(AIMove)
                move_made = True
                animate = True
                AIThinking = False

        if move_made:
            if animate:
                animateMove(game_state.moveLog[-1], screen, game_state, clock)
            valid_moves = game_state.getValidMoves_2()
            move_made = False
            animate = False
            moveUndone = False

        draw_game_state(screen, game_state, valid_moves, sq_selected)

        if game_state.checkMate:
            game_over = True
            if game_state.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif game_state.staleMate:
            game_over = True
            stringWin = "Black wins by stalemate" if game_state.whiteToMove else "White wins by stalemate"
            drawText(screen, stringWin)

        # Điều chỉnh tốc độ của khung hinh
        # Đảm bảo rằng mỗi lần vòng lặp thực hiện, thời gian giữa các khung hình liên tiếp sẽ ít nhất là 1/MAX_FPS giây.
        clock.tick(MAX_FPS)

        # Cập nhật lại màn hình
        p.display.flip()


def highlight_squares(screen, game_state, valid_moves, sq_selected):
    """
    Highlight ô đã chọn và các ô có thể di chuyển
    """
    if sq_selected != ():
        row, column = sq_selected
        if game_state.board[row][column][0] == ("w" if game_state.whiteToMove else "b"):
            # Vẽ hình chữ nhật xanh lá cây cho ô đã chọn
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Độ trong suốt
            s.fill(p.Color("blue"))
            screen.blit(s, (column * SQ_SIZE, row * SQ_SIZE))
            # Vẽ các nước đi hợp lệ
            s.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.startRow == row and move.startColumn == column:
                    screen.blit(
                        s, (move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE)
                    )

def highlight_inCheck_king(screen, game_state):
    # Tô cảnh báo màu đỏ cho quân vua trên bàn cờ đội địch nếu bị đang inCheck
    if game_state.inCheck:
        if game_state.whiteToMove:
            # Highlight màu đỏ tại quân vua của đội trắng
            white_king_location = game_state.whiteKingLocation
            s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            s.fill(p.Color(255, 0, 0, 100))
            screen.blit(s, (white_king_location[1] * SQ_SIZE, white_king_location[0] * SQ_SIZE))
            screen.blit(IMAGES["wK"], (white_king_location[1] * SQ_SIZE, white_king_location[0] * SQ_SIZE))
        else:
            # Highlight màu đỏ tại quân vua của đội đen
            black_king_location = game_state.blackKingLocation
            s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            s.fill(p.Color(255, 0, 0, 100))
            screen.blit(s, (black_king_location[1] * SQ_SIZE, black_king_location[0] * SQ_SIZE))
            screen.blit(IMAGES["bK"], (black_king_location[1] * SQ_SIZE, black_king_location[0] * SQ_SIZE))

def animateMove(move, screen, game_state, clock):
    global colors
    coords = []  # List chứa các tọa độ của các ô cần di chuyển
    dR = move.endRow - move.startRow
    dC = move.endColumn - move.startColumn
    framesPerSquare = 10  # Frames để di chuyển 1 ô
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startColumn + dC * frame / frameCount)
        draw_board(screen)
        draw_pieces(screen, game_state.board)
        # Xóa quân cờ tại ô cũ
        color = colors[(move.endRow + move.endColumn) % 2]
        endSquare = p.Rect(move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Vẽ quân cờ tại ô mới
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        
        # Vẽ quân cờ di chuyển
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 50, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

def draw_board(screen):
    """
    Vẽ các hình vuông cho bàn cờ,
    """
    global colors
    colors = [p.Color("#ebecd0"), p.Color("#739552")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row + column) % 2]
            p.draw.rect(
                screen,
                color,
                p.Rect(
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
                    p.Rect(
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
    highlight_inCheck_king(screen, game_state)  # Highlight quân vua nếu bị chiếu

if __name__ == "__main__":
    main()