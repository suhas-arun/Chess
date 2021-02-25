"""Flask webapp"""

from flask import Flask, render_template, request, redirect
from chess_engine import Game, Pawn, Queen, Rook, Bishop, Knight

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"

app.debug = True

GAME = Game()
GAME.board.initialise_board()


@app.route("/")
def play():
    """2 player game"""
    return render_template(
        "board.html",
        board=GAME.board.board,
        current_move=GAME.current_move,
        current_player=GAME.current_player_colour,
        show_promotion=GAME.show_promotion_box,
        white_pieces_taken=GAME.board.white_pieces_taken,
        black_pieces_taken=GAME.board.black_pieces_taken,
        result=(GAME.white_checkmate, GAME.black_checkmate, GAME.stalemate)
    )


@app.route("/move", methods=["GET", "POST"])
def move():
    """
    When a square on the board is clicked, a post request is made, returning
    the row and column of the square that was clicked. After a second square
    is clicked
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
            if isinstance(piece, Pawn) and (
                piece.colour and row == 0 or not piece.colour and row == 7
            ):
                GAME.show_promotion_box = True
                GAME.promotion_square = (row, column)

            GAME.is_checkmate_or_stalemate()
            GAME.check_draw()

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

    piece_type = request.args.get("piece")
    piece_class = globals()[piece_type]
    new_piece = piece_class(row, column, colour)
    if colour:
        GAME.board.white_pieces.remove(pawn)
        GAME.board.white_pieces.append(new_piece)
    else:
        GAME.board.black_pieces.remove(pawn)
        GAME.board.black_pieces.append(new_piece)

    GAME.board.board[row][column] = new_piece
    GAME.show_promotion_box = False
    GAME.promotion_square = ()
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
    print(player, str(GAME.current_player_colour))
    if player == str(GAME.current_player_colour):
        if player == "True":
            GAME.black_checkmate = True
        else:
            GAME.white_checkmate = True
    
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
