import pygame as p
import ChessEngine

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

    screen = p.display.set_mode(size=(WIDTH, HEIGHT))
    p.display.set_caption("Chess AI")

    # Màn hình game
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves_2()
    move_made = False # Biến cờ trạng thái khi thực hiện 1 nước đi

    load_images()

    running = True
    sq_selected = ()  # Lưu trữ click cuối cùng of người chơi
    player_clicks = []  # Lưu giữ click của người dùng (click đầu, và cuối khi chọn 1 ô)

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
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
                            game_state.makeMove(valid_moves[i])
                            move_made = True
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
            
        if move_made:
            valid_moves = game_state.getValidMoves_2()
            move_made = False
        draw_game_state(screen, game_state)

        # Điều chỉnh tốc độ của khung hinh
        # Đảm bảo rằng mỗi lần vòng lặp thực hiện, thời gian giữa các khung hình liên tiếp sẽ ít nhất là 1/MAX_FPS giây.
        clock.tick(MAX_FPS)

        # Cập nhật lại màn hình
        p.display.flip()


def draw_board(screen):
    """
    Vẽ các hình vuông cho bàn cờ,
    """
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


def draw_game_state(screen, game_state):
    draw_board(screen)  # Vẽ bàn cờ
    draw_pieces(screen, game_state.board)  # Vẽ các quân cờ vào


if __name__ == "__main__":
    main()
