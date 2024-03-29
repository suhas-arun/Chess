"""Flask webapp"""


from flask import Flask, render_template, request, redirect
from chess_engine import Game, Pawn, Queen, Rook, Bishop, Knight
from ai import AI

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"


GAME = Game()
GAME.board.initialise_board()
ai = AI()


@app.route("/")
def play():
    """Renders the board template and allows the game to be played"""
    return render_template(
        "board.html",
        board=GAME.board.board,
        current_move=GAME.current_move,
        current_player=GAME.current_player_colour,
        show_promotion=GAME.show_promotion_box,
        white_pieces_taken=GAME.board.white_pieces_taken,
        black_pieces_taken=GAME.board.black_pieces_taken,
        result=(GAME.white_checkmate, GAME.black_checkmate, GAME.stalemate),
        aimove=GAME.ai_colour == GAME.current_player_colour,
        start_menu=not GAME.in_progress,
    )


@app.route("/move", methods=["GET", "POST"])
def move():
    """
    When a square on the board is clicked, a post request is made, returning
    the row and column of the square that was clicked. After a second square
    is clicked the two squares form a move, which is validated and executed.
    """
    if GAME.show_promotion_box:
        return redirect("/")

    column = int(request.args.get("column")) - 1
    row = int(request.args.get("row")) - 1
    new_square = (row, column)

    if len(GAME.current_move) == 1:  # The piece is being moved to the new square
        current_square = GAME.current_move[0]
        if GAME.validate_move(current_square, new_square):
            GAME.execute_move(current_square, new_square)
            piece = GAME.board.board[row][column]
            # Promote pawn
            if isinstance(piece, Pawn) and (
                piece.colour and row == 0 or not piece.colour and row == 7
            ):
                GAME.show_promotion_box = True
                GAME.promotion_square = (row, column)
                return redirect("/")

            GAME.is_checkmate_or_stalemate()
            GAME.check_draw()

            # Display result
            if GAME.white_checkmate or GAME.black_checkmate or GAME.stalemate:
                return redirect("/")

            GAME.current_move.append(new_square)
        else:
            GAME.current_move = []
            if GAME.board.board[row][column]:
                GAME.current_move.append(new_square)

    else:  # The piece to be moved is on the new square
        GAME.current_move = []
        GAME.current_move.append(new_square)

    return redirect("/")


@app.route("/promote", methods=["GET", "POST"])
def promote():
    """Promotes a pawn to a new piece"""
    row, column = GAME.promotion_square
    colour = not GAME.current_player_colour
    pawn = GAME.board.board[row][column]

    # Create new piece object
    piece_type = request.args.get("piece")
    piece_class = globals()[piece_type]
    new_piece = piece_class(row, column, colour)
    if colour:
        GAME.board.white_pieces.remove(pawn)
        GAME.board.white_pieces.append(new_piece)
    else:
        GAME.board.black_pieces.remove(pawn)
        GAME.board.black_pieces.append(new_piece)

    # Put piece on board
    GAME.board.board[row][column] = new_piece
    GAME.show_promotion_box = False
    GAME.promotion_square = ()

    if GAME.current_player_colour == GAME.ai_colour:
        if GAME.white_checkmate or GAME.black_checkmate or GAME.stalemate:
            return redirect("/")

        return redirect("/aimove")

    return redirect("/")


@app.route("/rematch")
def rematch():
    """Restarts the game"""
    global GAME
    GAME = Game()
    GAME.board.initialise_board()
    return redirect("/")


@app.route("/resign", methods=["GET", "POST"])
def resign():
    """
    When the resign button is clicked, a post request is
    made, returning the colour of the player resigning. If
    this player is the current player then they have lost.
    """

    player = request.args.get("player")
    if player == str(GAME.current_player_colour):
        if player == "True":
            GAME.black_checkmate = True
        else:
            GAME.white_checkmate = True

    return redirect("/")


@app.route("/aimove")
def aimove():
    """Allows the AI to make a move after the user."""

    # Call the AI method to get best move
    # current_square, new_square = ai.get_greedy_ai_move(GAME)
    ai.get_ai_move_minimax(GAME, AI.DEPTH, GAME.current_player_colour)
    moves = ai.minimax_best_moves
    if moves:
        current_square, new_square = ai.get_random_move(moves)
        while not GAME.validate_move(current_square, new_square):
            current_square, new_square = ai.get_random_move(moves)
    else:
        current_square, new_square = ai.get_random_move(GAME.get_valid_moves())

    GAME.execute_move(current_square, new_square)
    row, column = new_square
    piece = GAME.board.board[row][column]
    # Pawn promotion
    if isinstance(piece, Pawn) and (
        piece.colour and row == 0 or not piece.colour and row == 7
    ):
        GAME.promotion_square = (new_square[0], new_square[1])
        return redirect("/promote?piece=Queen")

    GAME.is_checkmate_or_stalemate()
    GAME.check_draw()

    GAME.current_move = [current_square, new_square]

    return redirect("/")


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Sets up the game."""
    global GAME
    game_mode = request.args.get("mode")
    GAME = Game()
    GAME.board.initialise_board()
    GAME.in_progress = True
    if game_mode == "2player":
        GAME.ai_game = False
        GAME.ai_colour = None
    elif game_mode == "aiwhite":
        GAME.ai_game = True
        GAME.ai_colour = False
    elif game_mode == "aiblack":
        GAME.ai_game = True
        GAME.ai_colour = True
        return redirect("/aimove")

    return redirect("/")


if __name__ == "__main__":
    app.run()
