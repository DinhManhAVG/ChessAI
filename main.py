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
        print
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
    load_images()

    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

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
